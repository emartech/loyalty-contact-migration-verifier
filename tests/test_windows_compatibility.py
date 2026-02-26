"""
Tests to ensure Windows compatibility across the codebase.
Verifies encoding is specified for file operations and ANSI colors are handled.
"""

import ast
import os
import re
from pathlib import Path

import pytest


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


class TestFileEncodingSpecified:
    """Tests to ensure all text file operations specify encoding."""

    def test_all_text_file_opens_specify_encoding(self):
        """
        Ensure all open() calls for text files specify encoding='utf-8'.
        
        On Windows, the default encoding is often cp1252, not UTF-8.
        This can cause UnicodeDecodeError or corrupt characters.
        Binary mode ('rb', 'wb') is exempt as it doesn't use encoding.
        """
        python_files = get_python_files()
        violations = []
        
        for file_path in python_files:
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        # Check if it's an open() call
                        if isinstance(node.func, ast.Name) and node.func.id == 'open':
                            # Get the mode argument (default is 'r' which is text mode)
                            mode = 'r'  # default
                            has_encoding = False
                            
                            # Check positional args for mode
                            if len(node.args) >= 2:
                                if isinstance(node.args[1], ast.Constant):
                                    mode = node.args[1].value
                            
                            # Check keyword args
                            for keyword in node.keywords:
                                if keyword.arg == 'mode':
                                    if isinstance(keyword.value, ast.Constant):
                                        mode = keyword.value.value
                                elif keyword.arg == 'encoding':
                                    has_encoding = True
                            
                            # Skip binary modes
                            if 'b' in str(mode):
                                continue
                            
                            # Text mode without encoding specified
                            if not has_encoding:
                                rel_path = file_path.relative_to(get_project_root())
                                violations.append(
                                    f"{rel_path}:{node.lineno}: open() without encoding"
                                )
            except SyntaxError:
                pass  # Skip files with syntax errors
            except UnicodeDecodeError:
                pass  # Skip files that can't be decoded
        
        if violations:
            violation_report = "\n".join(violations)
            pytest.fail(
                f"Found {len(violations)} open() call(s) without explicit encoding:\n"
                f"{violation_report}\n\n"
                "Please add encoding='utf-8' to all text file open() calls for Windows compatibility."
            )


class TestWindowsColorSupport:
    """Tests to ensure ANSI colors work on Windows."""

    def test_windows_ansi_support_enabled(self):
        """
        Ensure Windows ANSI/VT100 support is enabled when using color codes.
        
        Windows 10+ supports ANSI codes but requires enabling VT100 mode.
        This is typically done with: os.system('') or via colorama.init()
        """
        watcher_path = get_project_root() / "watcher.py"
        
        if not watcher_path.exists():
            pytest.skip("watcher.py not found")
        
        content = watcher_path.read_text(encoding='utf-8')
        
        # Check if ANSI codes are used
        uses_ansi = bool(re.search(r"\\033\[|\\x1b\[", content))
        
        if not uses_ansi:
            pytest.skip("No ANSI color codes found")
        
        # Check for Windows compatibility measures
        has_colorama = 'colorama' in content
        has_system_call = "os.system('')" in content or 'os.system("")' in content
        has_platform_check = 'platform.system' in content or 'sys.platform' in content
        
        if not (has_colorama or has_system_call or has_platform_check):
            pytest.fail(
                "watcher.py uses ANSI color codes but has no Windows compatibility.\n\n"
                "Add one of the following at the start of the script:\n"
                "  1. import os; os.system('')  # Enables VT100 on Windows 10+\n"
                "  2. import colorama; colorama.init()  # Third-party but more robust\n"
                "  3. Platform check to disable colors on unsupported Windows"
            )

    def test_color_class_has_disable_option_or_platform_handling(self):
        """
        Colors should be disable-able or handle platforms that don't support them.
        """
        watcher_path = get_project_root() / "watcher.py"
        
        if not watcher_path.exists():
            pytest.skip("watcher.py not found")
        
        content = watcher_path.read_text(encoding='utf-8')
        
        # Check if there's a Colors class
        if 'class Colors' not in content:
            pytest.skip("No Colors class found")
        
        # Should have some way to handle unsupported terminals
        # Either colorama, platform check, or environment variable check
        has_fallback = any([
            'colorama' in content,
            'platform.system' in content,
            'sys.platform' in content,
            "os.system('')" in content,
            'os.system("")' in content,
            'NO_COLOR' in content,  # Standard env var for disabling colors
            'TERM' in content,
        ])
        
        if not has_fallback:
            pytest.fail(
                "Colors class exists but has no platform/terminal fallback.\n"
                "Windows cmd.exe (pre-Win10) doesn't support ANSI codes.\n\n"
                "Add: import os; os.system('')  # Enable VT100 mode on Windows 10+"
            )
