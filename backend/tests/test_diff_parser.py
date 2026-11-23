"""Unit tests for Unified Git Diff parsing and line number extraction."""

import pytest
from backend.app.services.github.diff_parser import parse_diff

SAMPLE_DIFF = """diff --git a/services/payment.py b/services/payment.py
index abc1234..def5678 100644
--- a/services/payment.py
+++ b/services/payment.py
@@ -10,6 +10,8 @@ def process_transaction(amount: float, currency: str):
     if amount <= 0:
         raise ValueError("Invalid amount")
+    if currency != "USD":
+        raise ValueError("Unsupported currency")
     return execute_payment(amount)
"""


def test_parse_diff_single_python_file():
    parsed = parse_diff(SAMPLE_DIFF)
    assert len(parsed.files) == 1
    file = parsed.files[0]
    assert file.filename == "services/payment.py"
    assert file.is_python is True
    assert file.additions == 2
    assert file.deletions == 0
    assert len(file.hunks) == 1

    hunk = file.hunks[0]
    assert hunk.new_start == 10
    # Added lines should be lines 12 and 13
    assert file.added_line_numbers == [12, 13]


def test_parse_diff_empty():
    parsed = parse_diff("")
    assert len(parsed.files) == 0


def test_parse_diff_multiple_files_with_non_python():
    multi_diff = """diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1,3 +1,4 @@
 # Project
+Documentation update
diff --git a/app/main.py b/app/main.py
--- a/app/main.py
+++ b/app/main.py
@@ -5,3 +5,4 @@ def run():
     pass
+    print("started")
"""
    parsed = parse_diff(multi_diff)
    assert len(parsed.files) == 2
    assert len(parsed.python_files) == 1
    assert parsed.python_files[0].filename == "app/main.py"
    assert parsed.total_additions == 2

