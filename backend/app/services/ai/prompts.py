"""Prompt templates and builders for SLM and LLM code review."""

import json
from typing import List, Optional
from backend.app.schemas.findings import StaticFinding

REVIEW_SYSTEM_PROMPT = """You are ReviewPilot AI, a rigorous, evidence-grounded Python code review system.
Your mission is to find genuine bugs, security flaws, and edge-case exceptions in the modified Python code.

RULES:
1. Output valid, parseable JSON ONLY. Do not include markdown ticks (```json), conversational text, or introductions.
2. Focus strictly on actionable defects: boundary conditions, NoneType errors, unhandled exceptions, type mismatches, off-by-one errors, resource leaks, or security vulnerabilities.
3. Every finding MUST specify:
   - "rule_id": short uppercase code (e.g., "NULL_POINTER", "INDEX_OUT_OF_BOUNDS", "ZERO_DIVISION", "TYPE_ERROR")
   - "category": "bug", "security", or "quality"
   - "severity": "CRITICAL", "HIGH", "MEDIUM", or "LOW"
   - "file_path": exact file path provided
   - "line_number": exact integer line number where the issue exists
   - "description": precise explanation of why the code fails
   - "self_confidence": float between 0.1 and 1.0 representing your certainty
   - "suspected_trigger_input": concrete Python input or argument that triggers the bug
   - "expected_behavior": what the code should do vs what it actually does
   - "suggested_test_assertion": an assert statement reproducing the failure
4. If no genuine defects exist, return an empty list: {"hypotheses": []}. Never hallucinate non-existent issues.

JSON SCHEMA:
{
  "hypotheses": [
    {
      "rule_id": "ZERO_DIVISION",
      "category": "bug",
      "severity": "HIGH",
      "file_path": "math_utils.py",
      "line_number": 15,
      "description": "Division by zero occurs when divisor is 0 without checking.",
      "self_confidence": 0.9,
      "suspected_trigger_input": "divisor = 0",
      "expected_behavior": "Should raise ValueError or handle zero safely",
      "suggested_test_assertion": "assert calculate(10, 0) != ZeroDivisionError"
    }
  ]
}
"""


def build_review_user_prompt(
    file_path: str,
    source_code: str,
    modified_lines: List[int],
    static_findings: Optional[List[StaticFinding]] = None,
) -> str:
    """Format the user prompt with source code, diff line numbers, and existing static findings."""
    static_summary = ""
    if static_findings:
        findings_text = "\n".join(
            [f"- Line {f.line_number} [{f.rule_id}]: {f.description}" for f in static_findings]
        )
        static_summary = f"\nStatic Analysis Warnings Detected:\n{findings_text}\n"

    diff_lines_str = ", ".join(map(str, modified_lines)) if modified_lines else "Full file"

    prompt = f"""Target File: {file_path}
Modified Lines in Pull Request: [{diff_lines_str}]
{static_summary}
Source Code to Review:
----------------------------------------
{source_code}
----------------------------------------

Analyze the code above and return JSON with any defect hypotheses.
"""
    return prompt

