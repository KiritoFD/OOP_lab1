# HTML Editor Project Structure Fixer

Write-Host "HTML Editor Project Structure Fixer" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "Using $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please ensure Python is installed and added to PATH." -ForegroundColor Red
    Exit
}

Write-Host "This script will reorganize your project structure."
Write-Host "WARNING: This will move files and update import paths." -ForegroundColor Yellow
$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne "y") {
    Exit
}

Write-Host "`nCreating directories..." -ForegroundColor Cyan

# Create directory structure
$directories = @(
    "src\commands\edit",
    "src\commands\display",
    "src\commands\io",
    "src\commands\session",
    "src\core",
    "src\plugins",
    "src\spellcheck",
    "tests\unit",
    "tests\integration",
    "docs\design"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory | Out-Null
        Write-Host "  Created: $dir"
    } else {
        Write-Host "  Already exists: $dir"
    }
}

Write-Host "`nMoving files..." -ForegroundColor Cyan

# File mapping (source -> destination)
$fileMap = @{
    "src\commands\display_commands.py" = "src\commands\display\commands.py"
    "src\commands\io_commands.py" = "src\commands\io\commands.py"
    "src\commands\session_commands.py" = "src\commands\session\commands.py"
    "test_comprehensive.py" = "tests\integration\test_comprehensive.py"
    "test_session.py" = "tests\integration\test_session.py"
    "test_enhanced_display.py" = "tests\unit\test_enhanced_display.py"
}

foreach ($sourceFile in $fileMap.Keys) {
    $destFile = $fileMap[$sourceFile]
    if (Test-Path $sourceFile) {
        Copy-Item -Path $sourceFile -Destination $destFile -Force
        Write-Host "  Copied: $sourceFile -> $destFile"
    } else {
        Write-Host "  Source not found: $sourceFile" -ForegroundColor Yellow
    }
}

Write-Host "`nCreating __init__.py files..." -ForegroundColor Cyan

# Init file content mapping
$initFiles = @{
    "src\__init__.py" = '"""HTML Editor source code package"""'
    "src\commands\__init__.py" = '"""Commands module"""'
    "src\commands\edit\__init__.py" = '"""Edit commands module"""'
    "src\commands\display\__init__.py" = @'
"""Display commands module - Provides HTML tree structure display and spell checking"""
from src.commands.display.commands import PrintTreeCommand, SpellCheckCommand

__all__ = ["PrintTreeCommand", "SpellCheckCommand"]
'@
    "src\commands\io\__init__.py" = '"""IO commands module"""'
    "src\commands\session\__init__.py" = '"""Session commands module"""'
    "src\core\__init__.py" = '"""Core module"""'
    "src\plugins\__init__.py" = '"""Plugins module"""'
    "src\spellcheck\__init__.py" = '"""Spellcheck module"""'
    "tests\__init__.py" = '"""Tests package"""'
    "tests\unit\__init__.py" = '"""Unit tests package"""'
    "tests\integration\__init__.py" = '"""Integration tests package"""'
}

foreach ($file in $initFiles.Keys) {
    Set-Content -Path $file -Value $initFiles[$file]
    Write-Host "  Created: $file"
}

Write-Host "`nRunning Python import updater..." -ForegroundColor Cyan

# Create a temporary Python script to update imports
$updateScript = @'
import os
import re

def update_imports(file_path):
    print(f"Updating: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original = content
    
    replacements = [
        (r'from src\.commands import display_commands', r'from src.commands.display import commands as display_commands'),
        (r'from src\.commands\.display_commands import (\w+)', r'from src.commands.display.commands import \1'),
        (r'from src\.commands import io_commands', r'from src.commands.io import commands as io_commands'),
        (r'from src\.commands\.io_commands import (\w+)', r'from src.commands.io.commands import \1'),
        (r'from src\.commands import session_commands', r'from src.commands.session import commands as session_commands'),
        (r'from src\.commands\.session_commands import (\w+)', r'from src.commands.session.commands import \1'),
        (r'from src\.commands\.edit\.(\w+)_command import (\w+Command)', r'from src.commands.edit.\1 import \2'),
        (r'from src\.commands\.edit import (\w+)_command', r'from src.commands.edit import \1'),
        (r'from src\.plugins import (\w+)', r'from src.plugins.\1 import \1'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  - Updated imports")

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py'):
            update_imports(os.path.join(root, file))
'@

Set-Content -Path "update_imports.py" -Value $updateScript
python update_imports.py
Remove-Item "update_imports.py"

Write-Host "`nProject structure fixed successfully!" -ForegroundColor Green
Write-Host "`nNext steps:"
Write-Host "1. Review the changes to ensure everything is correct"
Write-Host "2. Run your tests to verify functionality"

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
