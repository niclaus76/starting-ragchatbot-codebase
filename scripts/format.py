#!/usr/bin/env python3
"""
Code formatting script using Black and isort.
Automatically formats all Python files in the project.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return whether it succeeded."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stderr if e.stderr else e.stdout)
        return False


def main():
    """Main formatting function."""
    print("🎨 Code Formatting Tool")
    print("======================")
    
    success = True
    
    # Run isort
    success &= run_command(
        ["uv", "run", "isort", "backend/", "main.py", "scripts/"],
        "Sorting imports with isort"
    )
    
    # Run Black
    success &= run_command(
        ["uv", "run", "black", "backend/", "main.py", "scripts/"],
        "Formatting code with Black"
    )
    
    if success:
        print("\n✨ All formatting completed successfully!")
        return 0
    else:
        print("\n❌ Some formatting operations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())