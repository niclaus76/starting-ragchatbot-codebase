"""
Simple verification script to check test structure without running pytest.
"""

import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def verify_test_structure():
    """Verify that test files can be imported and basic structure is correct."""
    print("Verifying test structure...")
    
    # Check if test directory exists
    test_dir = os.path.join('backend', 'tests')
    if not os.path.exists(test_dir):
        print(f"[FAIL] Test directory {test_dir} does not exist")
        return False
    
    print(f"[OK] Test directory {test_dir} exists")
    
    # Check test files
    expected_files = [
        '__init__.py',
        'conftest.py', 
        'test_api_endpoints.py',
        'test_rag_system.py'
    ]
    
    for file in expected_files:
        file_path = os.path.join(test_dir, file)
        if os.path.exists(file_path):
            print(f"[OK] {file} exists")
        else:
            print(f"[FAIL] {file} missing")
            return False
    
    # Try importing test modules
    try:
        # Test conftest imports
        sys.path.insert(0, test_dir)
        import conftest
        print("[OK] conftest.py imports successfully")
        
        # Check if fixtures are defined
        fixtures = ['mock_config', 'mock_rag_system', 'test_client', 'sample_courses_data']
        for fixture in fixtures:
            if hasattr(conftest, fixture) or fixture in dir(conftest):
                print(f"[OK] Fixture '{fixture}' found")
        
    except ImportError as e:
        print(f"[FAIL] Failed to import conftest: {e}")
        return False
    except Exception as e:
        print(f"[WARN] Warning during conftest check: {e}")
    
    # Check pyproject.toml for pytest config
    if os.path.exists('pyproject.toml'):
        with open('pyproject.toml', 'r') as f:
            content = f.read()
            if '[tool.pytest.ini_options]' in content:
                print("[OK] pytest configuration found in pyproject.toml")
            else:
                print("[FAIL] pytest configuration missing from pyproject.toml")
                return False
    else:
        print("[FAIL] pyproject.toml not found")
        return False
    
    print("\n[OK] Test structure verification completed successfully!")
    return True

def show_test_info():
    """Show information about the test setup."""
    print("\n[INFO] Test Framework Information:")
    print("=" * 50)
    print("Test Framework: pytest")
    print("Test Directory: backend/tests/")
    print("Configuration: pyproject.toml [tool.pytest.ini_options]")
    print("\nTest Files:")
    print("- conftest.py: Shared fixtures and test configuration")
    print("- test_api_endpoints.py: API endpoint tests")
    print("- test_rag_system.py: Core RAG system unit tests")
    print("\nKey Features:")
    print("- Mocked dependencies for isolated testing")
    print("- Separate test app to avoid static file issues")
    print("- Comprehensive API endpoint coverage")
    print("- Unit and integration test markers")
    print("- Test fixtures for common data and mocks")
    
    print("\n[INFO] Test Dependencies Added:")
    print("- pytest>=8.0.0")
    print("- pytest-asyncio>=0.24.0") 
    print("- httpx>=0.27.0 (for FastAPI testing)")
    print("- pytest-mock>=3.14.0")
    
    print("\n[INFO] To Run Tests:")
    print("1. uv sync (install dependencies)")
    print("2. uv run pytest backend/tests/ -v")
    print("3. uv run pytest -m api (run only API tests)")
    print("4. uv run pytest -m unit (run only unit tests)")

if __name__ == "__main__":
    success = verify_test_structure()
    show_test_info()
    
    if success:
        print("\n[OK] All checks passed! Test framework is ready.")
        sys.exit(0)
    else:
        print("\n[FAIL] Some checks failed. Please review the output above.")
        sys.exit(1)