"""Docker Sandbox Runner for executing generated tests in restricted ephemeral containers."""

import os
import re
import shutil
import tempfile
import time
from typing import Optional
import docker
from docker.errors import DockerException
from backend.app.config import settings
from backend.app.schemas.execution import ExecutionRequest, ExecutionResult


def classify_pytest_output(exit_code: int, stdout: str, stderr: str, timeout_reached: bool) -> tuple[str, Optional[str], Optional[str]]:
    """Classify execution output into actionable result statuses and extract exception info.

    Returns:
        (execution_status, exception_name, exception_details)
    """
    if timeout_reached:
        return "TIMEOUT", "TimeoutError", "Execution exceeded maximum allowed time limit."

    combined = f"{stdout}\n{stderr}"

    if exit_code == 0:
        return "PASS", None, None

    # Check for test syntax errors
    if "SyntaxError:" in combined:
        m = re.search(r"SyntaxError:\s*(.*)", combined)
        details = m.group(1).strip() if m else "Syntax error in test code"
        return "TEST_SYNTAX_ERROR", "SyntaxError", details

    # Check for missing imports
    if "ModuleNotFoundError:" in combined or "ImportError:" in combined:
        m = re.search(r"(?:ModuleNotFoundError|ImportError):\s*(.*)", combined)
        details = m.group(1).strip() if m else "Module import error"
        return "TEST_IMPORT_ERROR", "ImportError", details

    # Check for assertion failure
    if "AssertionError" in combined or "assert " in combined:
        m = re.search(r"E\s+(assert\s+.*|AssertionError.*)", combined)
        details = m.group(1).strip() if m else "Assertion failed"
        return "ASSERTION_FAILURE", "AssertionError", details

    # Check for general runtime exceptions (e.g. ZeroDivisionError, TypeError, ValueError, KeyError)
    exc_match = re.search(r"E\s+([A-Za-z0-9_]+Error|[A-Za-z0-9_]+Exception):\s*(.*)", combined)
    if exc_match:
        exc_name = exc_match.group(1).strip()
        exc_msg = exc_match.group(2).strip()
        return "RUNTIME_EXCEPTION", exc_name, exc_msg

    return "RUNTIME_EXCEPTION", "UnknownException", "Non-zero exit code with unclassified failure."


class DockerSandboxRunner:
    """Manages secure, containerized execution of generated pytest test suites."""

    def __init__(self):
        self.image = settings.DOCKER_IMAGE
        self.timeout = settings.DOCKER_EXECUTION_TIMEOUT_SECONDS
        self.memory_limit = settings.DOCKER_MEMORY_LIMIT
        self.cpu_limit = settings.DOCKER_CPU_LIMIT

    def is_docker_available(self) -> bool:
        """Check if local Docker engine daemon is responsive."""
        try:
            client = docker.from_env()
            client.ping()
            return True
        except Exception:
            return False

    def execute_test(self, req: ExecutionRequest) -> ExecutionResult:
        """Execute a generated test in an ephemeral Docker container."""
        if not self.is_docker_available():
            return ExecutionResult(
                execution_status="ENVIRONMENT_ERROR",
                exit_code=-1,
                stderr="Docker daemon is not running or unreachable. Please start Docker Desktop.",
            )

        # Create temporary directory for isolated workspace
        temp_dir = tempfile.mkdtemp(prefix="reviewpilot_sandbox_")
        container = None
        client = docker.from_env()

        try:
            # 1. Write target source files into workspace
            for filename, content in req.source_files.items():
                target_file_path = os.path.join(temp_dir, filename)
                os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
                with open(target_file_path, "w", encoding="utf-8") as f:
                    f.write(content)

            # 2. Write test file into workspace
            test_file_path = os.path.join(temp_dir, "test_generated.py")
            with open(test_file_path, "w", encoding="utf-8") as f:
                f.write(req.test_code)

            # 3. Spawn isolated container with strict limits
            start_time = time.perf_counter()
            container = client.containers.run(
                image=self.image,
                command=["pytest", "test_generated.py", "-v", "--tb=short"],
                working_dir="/workspace",
                volumes={temp_dir: {"bind": "/workspace", "mode": "rw"}},
                network_mode="none",  # Strict network isolation
                mem_limit=self.memory_limit,
                cpu_period=100000,
                cpu_quota=int(100000 * self.cpu_limit),
                user="1000:1000",
                security_opt=["no-new-privileges:true"],
                cap_drop=["ALL"],
                detach=True,
                remove=False,
            )

            # 4. Wait for execution with timeout
            timeout_occurred = False
            try:
                result = container.wait(timeout=self.timeout)
                exit_code = result.get("StatusCode", 1)
            except Exception:
                # Execution timed out
                timeout_occurred = True
                exit_code = 124
                try:
                    container.kill()
                except Exception:
                    pass

            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            # 5. Capture logs
            logs = container.logs(stdout=True, stderr=True)
            output_text = logs.decode("utf-8", errors="replace") if isinstance(logs, bytes) else str(logs)

            status, exc_name, exc_details = classify_pytest_output(
                exit_code=exit_code,
                stdout=output_text,
                stderr="",
                timeout_reached=timeout_occurred,
            )

            return ExecutionResult(
                execution_status=status,
                exit_code=exit_code,
                execution_time_ms=elapsed_ms,
                stdout=output_text,
                stderr="",
                exception_name=exc_name,
                exception_details=exc_details,
                timeout_reached=timeout_occurred,
                container_id=container.id[:12] if container else None,
            )

        except DockerException as e:
            return ExecutionResult(
                execution_status="ENVIRONMENT_ERROR",
                exit_code=-1,
                stderr=f"Docker execution error: {str(e)}",
            )
        finally:
            # 6. Ensure container is destroyed
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass
            # 7. Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)

