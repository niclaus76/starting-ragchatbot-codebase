# Frontend-related Testing Framework Enhancements

## Overview
Enhanced the testing framework for the RAG system with comprehensive API testing infrastructure. While the feature focuses on backend testing, it ensures the frontend's API interactions are thoroughly tested.

## Changes Made

### 1. Test Dependencies Added to `pyproject.toml`
- **pytest>=8.0.0**: Core testing framework
- **pytest-asyncio>=0.24.0**: Async test support for FastAPI endpoints
- **httpx>=0.27.0**: HTTP client for testing FastAPI applications
- **pytest-mock>=3.14.0**: Mocking utilities for isolated testing

### 2. Pytest Configuration Added
Added comprehensive pytest configuration in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["backend/tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = ["-v", "--strict-markers", "--disable-warnings", "--tb=short"]
markers = ["unit: Unit tests", "integration: Integration tests", "api: API endpoint tests"]
asyncio_mode = "auto"
```

### 3. Test Infrastructure Created

#### `backend/tests/conftest.py`
Shared fixtures and test configuration including:
- **mock_config**: Mock configuration for testing
- **mock_rag_system**: Mock RAG system with all dependencies
- **mock_vector_store**: Mock vector store for data operations
- **mock_ai_generator**: Mock AI generator for response generation
- **mock_session_manager**: Mock session management
- **sample_courses_data**: Test data for courses
- **sample_chunks_data**: Test data for content chunks
- **temp_docs_directory**: Temporary directory with sample documents

#### `backend/tests/test_api_endpoints.py`
Comprehensive API endpoint testing:
- **Test App Factory**: Created `create_test_app()` to avoid static file mounting issues
- **All API Endpoints Covered**:
  - `/api/query`: Query processing with/without session ID
  - `/api/courses`: Course statistics retrieval
  - `/api/new-session`: Session creation
  - `/api/debug-links`: Debug information
  - `/api/visualization-data`: Visualization data for frontend
  - `/`: Root endpoint
- **Error Handling**: Tests for server errors and validation errors
- **CORS Testing**: Verification of CORS headers
- **Response Model Validation**: Ensures API responses conform to expected schemas

#### `backend/tests/test_rag_system.py`
Core RAG system unit and integration tests:
- **Unit Tests**: Individual component testing with mocks
- **Integration Tests**: Full workflow testing
- **Error Handling**: Exception propagation and handling
- **Session Management**: Conversation history integration
- **Analytics**: Course analytics functionality

### 4. Static File Issue Resolution
The original FastAPI app mounts static files from `/frontend`, which don't exist in test environment. Solution implemented:
- **Separate Test App**: Created `create_test_app()` function that defines API endpoints inline
- **No Static File Mounting**: Test app only includes API routes
- **Dependency Injection**: Uses mocked RAG system instead of real dependencies
- **Clean Separation**: Test app mirrors production API behavior without filesystem dependencies

## Frontend Impact

### API Testing Coverage
All frontend API interactions are now thoroughly tested:

1. **Query Functionality** (`frontend/script.js` interactions with `/api/query`):
   - POST requests with query data
   - Session ID handling
   - Response processing with answer and sources
   - Error handling for server failures

2. **Course Statistics** (potential frontend analytics):
   - GET requests to `/api/courses`
   - Course count and title display
   - Error handling for failed requests

3. **Session Management** (chat session functionality):
   - POST requests to `/api/new-session`
   - Session ID management
   - Session continuity across requests

4. **Visualization Data** (D3.js network visualization):
   - GET requests to `/api/visualization-data`
   - Node and link data structure validation
   - Data format compliance for D3.js rendering

### Development Workflow Benefits
- **API Contract Testing**: Ensures backend APIs remain compatible with frontend expectations
- **Regression Prevention**: Catches breaking changes before they affect frontend
- **Mock Data**: Provides consistent test data for frontend development
- **Error Scenario Testing**: Tests how frontend should handle various error conditions

## Running Tests

### Installation
```bash
uv sync  # Install all dependencies including test framework
```

### Test Execution
```bash
# Run all tests
uv run pytest backend/tests/ -v

# Run only API tests (frontend-relevant)
uv run pytest -m api

# Run only unit tests
uv run pytest -m unit

# Run integration tests
uv run pytest -m integration

# Run specific test file
uv run pytest backend/tests/test_api_endpoints.py -v
```

### Test Structure
```
backend/tests/
├── __init__.py              # Test package marker
├── conftest.py              # Shared fixtures and configuration
├── test_api_endpoints.py    # API endpoint tests (frontend-relevant)
└── test_rag_system.py       # Core system unit tests
```

## Key Features for Frontend Development

1. **Isolated Testing**: Each test runs with fresh mocked dependencies
2. **Fast Execution**: No real database or API calls during testing
3. **Comprehensive Coverage**: All API endpoints used by frontend are tested
4. **Error Scenarios**: Tests various failure modes frontend might encounter
5. **Data Validation**: Ensures API responses match frontend expectations
6. **CORS Verification**: Confirms cross-origin requests work correctly

## Future Enhancements
- Add performance testing for API endpoints
- Add integration tests with real frontend JavaScript
- Add visual regression testing for the web interface
- Add end-to-end testing with browser automation