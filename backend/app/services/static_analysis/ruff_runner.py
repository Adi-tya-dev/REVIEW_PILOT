"""Programmatic runner for Ruff static code analyzer."""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional, Set
from backend.app.schemas.findings import StaticFinding


def categorize_ruff_rule(rule_code: str) -> tuple[str, str]:
    """Map a Ruff rule code to (category, severity).

    Categories: 'security', 'bug', 'quality'
    Severities: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    """
    rule = rule_code.upper()

    # Security rules (Flake8-bandit within Ruff)
    if rule.startswith("S"):
        return "security", "HIGH"

    # Definite logic / runtime bugs (Pyflakes, bugbear, flake8-async)
    if rule in ("F821", "F822", "F823", "F831", "F706", "F707"):
        return "bug", "HIGH"  # Undefined names, invalid return/yield
    if rule.startswith("B"):  # flake8-bugbear
        return "bug", "HIGH" if "006" in rule or "008" in rule else "MEDIUM"
    if rule.startswith("ASYNC"):
        return "bug", "HIGH"

    # Unused variables, imports, syntax quality
    if rule.startswith("F"):
        return "quality", "MEDIUM"
    if rule.startswith("E9") or rule.startswith("F7"):
        return "bug", "CRITICAL"  # Syntax error

    # Style and PEP8
    return "quality", "LOW"


async def run_ruff_on_path(
    target_path: Path,
    modified_line_numbers: Optional[Set[int]] = None,
) -> List[StaticFinding]:
    """Run Ruff against a file or directory and return structured findings.

    Args:
        target_path: Path to Python file or directory.
        modified_line_numbers: Optional set of 1-based line numbers modified in PR diff.

    Returns:
        List of StaticFinding objects.
    """
    if modified_line_numbers is None:
        modified_line_numbers = set()

    cmd = [
        sys.executable,
        "-m",
        "ruff",
        "check",
        str(target_path),
        "--output-format",
        "json",
        "--select",
        "E,W,F,B,S,ASYNC",  # Include errors, warnings, pyflakes, bugbear, bandit, async
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
    except Exception as e:
        return [
            StaticFinding(
                rule_id="RUFF_EXEC_ERROR",
                tool="ruff",
                category="quality",
                severity="LOW",
                file_path=str(target_path),
                line_number=1,
                description=f"Failed to execute Ruff: {str(e)}",
                is_in_diff=False,
            )
        ]

    findings: List[StaticFinding] = []
    if not stdout:
        return findings

    try:
        raw_items = json.loads(stdout.decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        return findings

    for item in raw_items:
        rule_code = item.get("code") or "RUFF_WARNING"
        message = item.get("message", "")
        filename = item.get("filename", str(target_path))

        location = item.get("location", {})
        line_num = location.get("row", 1)
        end_location = item.get("end_location", {})
        end_line_num = end_location.get("row", line_num)

        category, severity = categorize_ruff_rule(rule_code)
        is_in_diff = line_num in modified_line_numbers or bool(
            set(range(line_num, end_line_num + 1)).intersection(modified_line_numbers)
        )

        findings.append(
            StaticFinding(
                rule_id=rule_code,
                tool="ruff",
                category=category,
                severity=severity,
                file_path=filename,
                line_number=line_num,
                end_line_number=end_line_num,
                description=message,
                code_snippet=None,
                confidence=1.0,
                is_in_diff=is_in_diff,
            )
        )

    return findings

