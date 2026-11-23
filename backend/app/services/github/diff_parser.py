"""Unified git diff parser for extracting changed files, hunks, and line mappings."""

import re
from typing import List, Optional
from backend.app.schemas.github import ChangedLine, DiffHunk, ModifiedFile, ParsedDiff

# Regex for hunk headers: @@ -old_start[,old_lines] +new_start[,new_lines] @@ optional heading
HUNK_HEADER_REGEX = re.compile(
    r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@(?:.*)?$"
)
DIFF_GIT_REGEX = re.compile(r"^diff --git a/(.*) b/(.*)$")
NEW_FILE_REGEX = re.compile(r"^\+\+\+ (?:b/)?(.*)$")
OLD_FILE_REGEX = re.compile(r"^--- (?:a/)?(.*)$")


def parse_diff(raw_diff: str) -> ParsedDiff:
    """Parse a unified git diff into structured ModifiedFile objects.

    Args:
        raw_diff: Raw unified git diff string.

    Returns:
        ParsedDiff containing structured files, hunks, and changed line numbers.
    """
    if not raw_diff or not raw_diff.strip():
        return ParsedDiff(files=[])

    files: List[ModifiedFile] = []
    lines = raw_diff.splitlines()

    current_file: Optional[ModifiedFile] = None
    current_hunk: Optional[DiffHunk] = None
    old_line_num = 0
    new_line_num = 0

    idx = 0
    num_lines = len(lines)

    while idx < num_lines:
        line = lines[idx]

        # Check for start of a new file diff
        diff_git_match = DIFF_GIT_REGEX.match(line)
        if diff_git_match:
            if current_hunk and current_file:
                current_file.hunks.append(current_hunk)
                current_hunk = None
            if current_file:
                files.append(current_file)

            old_path = diff_git_match.group(1).strip()
            new_path = diff_git_match.group(2).strip()
            is_py = new_path.endswith(".py") or old_path.endswith(".py")

            current_file = ModifiedFile(
                filename=new_path,
                previous_filename=old_path if old_path != new_path else None,
                is_python=is_py,
                hunks=[],
                added_line_numbers=[],
            )
            idx += 1
            continue

        # File header lines (--- a/... or +++ b/...)
        if line.startswith("--- ") or line.startswith("+++ "):
            if line.startswith("+++ ") and current_file:
                m = NEW_FILE_REGEX.match(line)
                if m and m.group(1).strip() != "/dev/null":
                    current_file.filename = m.group(1).strip()
                    current_file.is_python = current_file.filename.endswith(".py")
            idx += 1
            continue

        # Check for hunk header
        hunk_match = HUNK_HEADER_REGEX.match(line)
        if hunk_match:
            if current_hunk and current_file:
                current_file.hunks.append(current_hunk)

            old_start = int(hunk_match.group(1))
            old_count = int(hunk_match.group(2)) if hunk_match.group(2) else 1
            new_start = int(hunk_match.group(3))
            new_count = int(hunk_match.group(4)) if hunk_match.group(4) else 1

            current_hunk = DiffHunk(
                header=line,
                old_start=old_start,
                old_lines=old_count,
                new_start=new_start,
                new_lines=new_count,
                lines=[],
            )
            old_line_num = old_start
            new_line_num = new_start
            idx += 1
            continue

        # Content lines inside a hunk
        if current_hunk and current_file:
            if line.startswith("+") and not line.startswith("+++"):
                content = line[1:]
                current_hunk.lines.append(
                    ChangedLine(
                        line_type="add",
                        content=content,
                        new_line_number=new_line_num,
                    )
                )
                current_file.additions += 1
                current_file.added_line_numbers.append(new_line_num)
                new_line_num += 1
            elif line.startswith("-") and not line.startswith("---"):
                content = line[1:]
                current_hunk.lines.append(
                    ChangedLine(
                        line_type="delete",
                        content=content,
                        old_line_number=old_line_num,
                    )
                )
                current_file.deletions += 1
                old_line_num += 1
            elif line.startswith(" "):
                content = line[1:]
                current_hunk.lines.append(
                    ChangedLine(
                        line_type="context",
                        content=content,
                        old_line_number=old_line_num,
                        new_line_number=new_line_num,
                    )
                )
                old_line_num += 1
                new_line_num += 1
            elif line == "":
                # Empty context line in some diff generators
                current_hunk.lines.append(
                    ChangedLine(
                        line_type="context",
                        content="",
                        old_line_number=old_line_num,
                        new_line_number=new_line_num,
                    )
                )
                old_line_num += 1
                new_line_num += 1

        idx += 1

    # Append trailing hunk and file
    if current_hunk and current_file:
        current_file.hunks.append(current_hunk)
    if current_file:
        files.append(current_file)

    return ParsedDiff(files=files)

