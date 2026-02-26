"""
Test to ensure no emojis or em dashes are used in the codebase.
This helps maintain consistent, portable console output across different terminals.
"""

import os
import re
from pathlib import Path

import pytest


# Unicode ranges for common emojis
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F9FF"  # Miscellaneous Symbols and Pictographs, Emoticons, etc.
    "\U00002600-\U000026FF"  # Miscellaneous Symbols
    "\U00002700-\U000027BF"  # Dingbats
    "\U0000231A-\U000023FF"  # Misc Technical (includes hourglass, watch, etc.)
    "\U00002B50-\U00002B55"  # Stars and circles
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F680-\U0001F6FF"  # Transport and Map Symbols
    "\U0001F1E0-\U0001F1FF"  # Flags
    "\U0000FE0F"             # Variation Selector-16 (emoji presentation)
    "]",
    flags=re.UNICODE
)

# Em dash, en dash, and other problematic dash characters
SPECIAL_DASH_PATTERN = re.compile(
    "["
    "\u2014"  # Em dash (U+2014)
    "\u2013"  # En dash (U+2013)
    "\u2012"  # Figure dash (U+2012)
    "\u2015"  # Horizontal bar (U+2015)
    "]"
)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_python_files() -> list[Path]:
    """Get all Python files in the project, excluding venv and cache directories."""
    project_root = get_project_root()
    python_files = []
    
    exclude_dirs = {'.venv', 'venv', '__pycache__', '.git', 'node_modules', '.tox', '.eggs'}
    
    for root, dirs, files in os.walk(project_root):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files


def find_violations(file_path: Path, pattern: re.Pattern, description: str) -> list[str]:
    """Find all violations of a pattern in a file."""
    violations = []
    try:
        content = file_path.read_text(encoding='utf-8')
        for line_num, line in enumerate(content.splitlines(), start=1):
            matches = pattern.findall(line)
            if matches:
                # Get relative path for cleaner output
                rel_path = file_path.relative_to(get_project_root())
                chars = ', '.join(repr(m) for m in matches)
                violations.append(f"{rel_path}:{line_num}: {description} found: {chars}")
    except UnicodeDecodeError:
        pass  # Skip files that can't be decoded as UTF-8
    return violations


class TestNoSpecialCharacters:
    """Tests to ensure no emojis or special dashes are used in the codebase."""

    def test_no_emojis_in_codebase(self):
        """Ensure no emoji characters are used in any Python files."""
        python_files = get_python_files()
        all_violations = []
        
        for file_path in python_files:
            violations = find_violations(file_path, EMOJI_PATTERN, "Emoji")
            all_violations.extend(violations)
        
        if all_violations:
            violation_report = "\n".join(all_violations)
            pytest.fail(
                f"Found {len(all_violations)} emoji violation(s) in the codebase:\n{violation_report}\n\n"
                "Please replace emojis with plain text alternatives."
            )

    def test_no_em_dashes_in_codebase(self):
        """Ensure no em dashes or en dashes are used in any Python files."""
        python_files = get_python_files()
        all_violations = []
        
        for file_path in python_files:
            violations = find_violations(file_path, SPECIAL_DASH_PATTERN, "Special dash")
            all_violations.extend(violations)
        
        if all_violations:
            violation_report = "\n".join(all_violations)
            pytest.fail(
                f"Found {len(all_violations)} special dash violation(s) in the codebase:\n{violation_report}\n\n"
                "Please replace em dashes and en dashes with regular hyphens (-)."
            )

    def test_python_files_exist(self):
        """Sanity check that we're actually scanning files."""
        python_files = get_python_files()
        assert len(python_files) > 0, "No Python files found to scan"
