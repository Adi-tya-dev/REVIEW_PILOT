"""Programmatic runner for Bandit security analysis."""

import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional, Set
from backend.app.schemas.findings import StaticFinding


async def run_bandit_on_path(
    target_path: Path,
    modified_line_numbers: Optional[Set[int]] = None,
) -> List[StaticFinding]:
    """Run Bandit security analyzer against a file or directory.

    Args:
        target_path: Path to Python file or directory.
        modified_line_numbers: Optional set of 1-based line numbers modified in PR diff.

    Returns:
        List of StaticFinding security objects.
    """
    if modified_line_numbers is None:
        modified_line_numbers = set()

    cmd = [
        sys.executable,
        "-m",
        "bandit",
        "-f",
        "json",
        "-q",
        str(target_path),
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
                rule_id="BANDIT_EXEC_ERROR",
                tool="bandit",
                category="security",
                severity="LOW",
                file_path=str(target_path),
                line_number=1,
                description=f"Failed to execute Bandit: {str(e)}",
                is_in_diff=False,
            )
        ]

    findings: List[StaticFinding] = []
    if not stdout:
        return findings

    try:
        data = json.loads(stdout.decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        return findings

    results = data.get("results", [])
    for item in results:
        test_id = item.get("test_id", "BANDIT_SECURITY_WARNING")
        issue_text = item.get("issue_text", "")
        severity = item.get("issue_severity", "MEDIUM").upper()
        confidence_str = item.get("issue_confidence", "HIGH").upper()
        filename = item.get("filename", str(target_path))
        line_num = item.get("line_number", 1)
        line_range = item.get("line_range", [line_num])
        code = item.get("code", "")

        conf_map = {"HIGH": 0.95, "MEDIUM": 0.75, "LOW": 0.5}
        conf_float = conf_map.get(confidence_str, 0.75)

        is_in_diff = bool(set(line_range).intersection(modified_line_numbers)) or (
            line_num in modified_line_numbers
        )

        findings.append(
            StaticFinding(
                rule_id=test_id,
                tool="bandit",
                category="security",
                severity=severity,
                file_path=filename,
                line_number=line_num,
                end_line_number=max(line_range) if line_range else line_num,
                description=issue_text,
                code_snippet=code.strip() if code else None,
                confidence=conf_float,
                is_in_diff=is_in_diff,
            )
        )

    return findings

