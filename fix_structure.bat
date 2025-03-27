@echo off
REM filepath: c:\Users\xy\Downloads\OOP_lab1\final_cleanup.bat

echo Starting final project cleanup...

REM *** Move application test files to app tests ***
echo Moving application test files...
if not exist tests\app mkdir tests\app
if exist tests\application\test_command_parser.py move tests\application\test_command_parser.py tests\app >nul 2>&1
if exist tests\application\__init__.py move tests\application\__init__.py tests\app >nul 2>&1
if exist tests\application rmdir tests\application >nul 2>&1
echo Application test files moved.

REM *** Move spell tests to proper location ***
echo Moving spell test files...
if not exist tests\spell\__init__.py type nul > tests\spell\__init__.py
if exist tests\spell\spellcheck\test_spellcheck.py move tests\spell\spellcheck\test_spellcheck.py tests\spell >nul 2>&1
if exist tests\spell\spellcheck\__pycache__ rmdir /s /q tests\spell\spellcheck\__pycache__ >nul 2>&1
if exist tests\spell\spellcheck rmdir tests\spell\spellcheck >nul 2>&1
echo Spell test files moved.

REM *** Create missing __init__.py files ***
echo Creating missing __init__.py files...
if not exist tests\core\__init__.py type nul > tests\core\__init__.py
echo Missing __init__.py files created.

REM *** Remove any remaining __pycache__ directories ***
echo Cleaning up __pycache__ directories...
for /d /r . %%d in (*__pycache__*) do (
    echo Removing %%d...
    rmdir /s /q "%%d" >nul 2>&1
)
echo __pycache__ directories cleaned.

echo Final project cleanup complete.
pause