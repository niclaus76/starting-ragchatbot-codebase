#!/usr/bin/env python3
"""
Code linting script using flake8 and other quality tools.
Checks code quality and reports issues.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str, allow_failure: bool = False) -> bool:
    """Run a command and return whether it succeeded."""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )
        print(f"✅ {description} passed")
        if result.stdout.strip():
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        if allow_failure:
            print(f"⚠️  {description} found issues:")
        else:
            print(f"❌ {description} failed:")
        
        output = e.stdout if e.stdout else e.stderr
        if output.strip():
            print(output)
        return False


def main():
    """Main linting function."""
    print("🔍 Code Quality Checker")
    print("=======================")
    
    success = True
    
    # Run flake8
    success &= run_command(
        ["uv", "run", "flake8", "backend/", "main.py", "scripts/"],
        "Checking code style with flake8",
        allow_failure=True
    )
    
    # Check import sorting
    success &= run_command(
        ["uv", "run", "isort", "--check-only", "--diff", "backend/", "main.py", "scripts/"],
        "Checking import sorting with isort",
        allow_failure=True
    )
    
    # Check code formatting
    success &= run_command(
        ["uv", "run", "black", "--check", "--diff", "backend/", "main.py", "scripts/"],
        "Checking code formatting with Black",
        allow_failure=True
    )
    
    if success:
        print("\n✨ All quality checks passed!")
        return 0
    else:
        print("\n⚠️  Some quality checks found issues. Run 'python scripts/format.py' to fix formatting issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())