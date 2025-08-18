@echo off
REM Code Quality Check Script for Windows
REM Runs all quality checks and formatting tools

echo 🚀 Running Code Quality Checks
echo ===============================

REM Navigate to project root
cd /d "%~dp0\.."

echo.
echo 📦 Installing/updating dependencies...
uv sync

echo.
echo 🎨 Running code formatting...
python scripts/format.py

echo.
echo 🔍 Running code quality checks...
python scripts/lint.py

echo.
echo ✨ Quality check complete!
pause