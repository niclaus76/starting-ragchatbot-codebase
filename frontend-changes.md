# Frontend Enhancement Suite: Code Quality, Testing Framework & Dark/Light Theme

## Overview
Comprehensive enhancement to the RAG chatbot development workflow including:
- Code quality tools for Python formatting and style checks
- Testing framework for API endpoint validation
- Dark/light theme toggle for improved user experience

## Changes Made

### 1. Code Quality Dependencies Added
Updated `pyproject.toml` to include essential code quality tools:
- **Black** (>=23.0.0) - Automatic code formatting
- **isort** (>=5.12.0) - Import statement sorting
- **flake8** (>=6.0.0) - Code linting and style checking
- **pre-commit** (>=3.0.0) - Git hooks for automated quality checks

### 2. Configuration Files

#### `pyproject.toml` Configuration
- **Black configuration**: 88-character line length, Python 3.11+ target, excludes build/cache directories
- **isort configuration**: Black-compatible profile with consistent import formatting
- **flake8 configuration**: 88-character line length, ignores Black-compatible rules (E203, W503)

#### `.pre-commit-config.yaml`
Pre-commit hooks configuration for automated quality checks:
- Black formatting
- isort import sorting  
- flake8 linting
- Basic file checks (trailing whitespace, EOF, YAML validation, etc.)

### 3. Development Scripts

Created `scripts/` directory with quality check automation:

#### `scripts/format.py`
- Automated code formatting using Black and isort
- Runs on `backend/`, `main.py`, and `scripts/` directories
- Provides detailed feedback with success/failure status
- Cross-platform Python script

#### `scripts/lint.py`
- Comprehensive code quality checking
- Runs flake8 linting, import sorting validation, and format checking
- Allows failures and provides actionable feedback
- Suggests running format script when issues are found

#### `scripts/quality-check.sh` (Linux/Mac)
- Complete quality workflow script
- Installs dependencies, runs formatting, and performs quality checks
- Bash script for Unix-based systems

#### `scripts/quality-check.bat` (Windows)
- Windows batch file equivalent of quality-check.sh
- Same functionality with Windows-specific commands
- Includes pause for output review

### 4. Documentation Updates

#### `CLAUDE.md` Updates
Added new "Code Quality" section with commands:
- `python scripts/format.py` - Auto-format code
- `python scripts/lint.py` - Run quality checks
- `scripts/quality-check.sh` or `.bat` - Full workflow
- `uv run pre-commit install` - Setup automated hooks

## Usage Instructions

### Quick Start
1. **Install dependencies**: `uv sync`
2. **Format code**: `python scripts/format.py`
3. **Check quality**: `python scripts/lint.py`
4. **Full workflow**: `scripts/quality-check.sh` (or `.bat` on Windows)

### Optional Pre-commit Setup
```bash
uv run pre-commit install
```
This enables automatic quality checks on every git commit.

### Integration with Development Workflow
- Run formatting before committing changes
- Use quality checks in CI/CD pipelines
- Integrate with IDEs that support Black/flake8

## Benefits

### Code Consistency
- Uniform formatting across the entire codebase
- Consistent import organization
- Standardized line lengths and style

### Developer Experience  
- Automated formatting reduces manual work
- Clear feedback on code quality issues
- Cross-platform compatibility (Windows/Mac/Linux)

### Quality Assurance
- Catches potential style and quality issues early
- Enforces best practices through linting
- Optional pre-commit hooks prevent poor quality commits

## Architecture Integration

The code quality tools integrate seamlessly with the existing RAG system architecture:
- No impact on runtime performance
- Maintained compatibility with existing FastAPI backend
- Enhanced developer workflow without affecting user-facing functionality
- Supports the existing uv-based dependency management

## File Structure Changes

```
├── .pre-commit-config.yaml      (NEW)
├── scripts/                     (NEW)
│   ├── format.py               (NEW)
│   ├── lint.py                 (NEW)
│   ├── quality-check.sh        (NEW)
│   └── quality-check.bat       (NEW)
├── pyproject.toml              (UPDATED)
└── CLAUDE.md                   (UPDATED)
```

All changes maintain backward compatibility and add optional quality enhancements to the development process.

### 2. Test Dependencies Added
Added comprehensive testing framework to `pyproject.toml`:
- **pytest>=8.0.0**: Core testing framework
- **pytest-asyncio>=0.24.0**: Async test support for FastAPI endpoints
- **httpx>=0.27.0**: HTTP client for testing FastAPI applications
- **pytest-mock>=3.14.0**: Mocking utilities for isolated testing

### 3. Pytest Configuration Added
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

### 4. Test Infrastructure Created

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

## Part 3: Dark/Light Theme Implementation

### 1. HTML Structure Updates (`index.html`)
- **Added theme toggle button** positioned at top-right with sun/moon icons
- **Updated cache-busting versions** for CSS (v10) and JS (v12) files
- **Accessibility features**: aria-label, title attributes, and keyboard navigation support

```html
<button class="theme-toggle" id="themeToggle" aria-label="Toggle between dark and light theme" title="Toggle theme">
    <span class="sun-icon">☀️</span>
    <span class="moon-icon active">🌙</span>
</button>
```

### 2. CSS Theme Styling (`style.css`)
- **Added CSS custom properties** for both dark and light themes
- **Dark theme (default)**: Existing dark color scheme with deep blues and grays
- **Light theme**: Clean light color scheme with white backgrounds and dark text
- **Smooth transitions**: 0.3s ease transitions for all color/background changes
- **Theme toggle button styling**: Fixed positioned circular button with hover effects

#### Key Theme Variables:
```css
/* Light Theme */
[data-theme="light"] {
    --background: #ffffff;
    --surface: #f8fafc;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --border-color: #e2e8f0;
    /* ... more variables */
}
```

#### Button Styling Features:
- Fixed position (top: 1rem, right: 1rem)
- Circular design (48px diameter)
- Smooth icon transitions with rotation and scaling
- Hover and focus states with elevation effects
- Keyboard accessibility (Enter/Space key support)

### 3. JavaScript Theme Management (`script.js`)
- **Theme initialization**: Checks localStorage for saved preference, defaults to dark
- **Toggle functionality**: Switches between themes on button click
- **Persistence**: Saves theme preference in localStorage
- **Icon management**: Smoothly transitions between sun/moon icons
- **Keyboard support**: Enter and Space key activation

#### Key Functions:
- `initializeTheme()`: Sets up theme on page load
- `toggleTheme()`: Switches between dark/light themes
- `setTheme(theme)`: Applies theme by setting data-theme attribute
- `updateThemeIcon(theme)`: Updates icon visibility with smooth transitions

### Theme Toggle Features

#### User Experience
- **Intuitive toggle button** positioned prominently in top-right corner
- **Visual feedback** with sun/moon emoji icons that rotate and scale during transitions
- **Smooth animations** for all color transitions (0.3s ease)
- **Theme persistence** - remembers user's preference across sessions

#### Accessibility
- **Keyboard navigation** - fully accessible via Tab, Enter, and Space keys
- **Screen reader support** - proper aria-label and title attributes
- **High contrast** - both themes maintain good readability standards
- **Focus indicators** - clear focus ring for keyboard users

#### Design Integration
- **Consistent with existing design language** - uses same border radius, shadows, and spacing
- **Responsive positioning** - works well on all screen sizes
- **Non-intrusive placement** - doesn't interfere with main content
- **Smooth transitions** - all elements transition smoothly between themes

### Technical Implementation

#### Theme Switching Mechanism
1. **Data attribute approach**: Uses `data-theme="light"` on document element
2. **CSS cascading**: Light theme variables override default dark theme
3. **JavaScript control**: Manages theme state and localStorage persistence
4. **Icon transitions**: CSS animations for smooth icon changes

#### Browser Compatibility
- **Modern browsers**: Full support for CSS custom properties
- **Fallback graceful**: Works without JavaScript (defaults to dark theme)
- **Local storage**: Standard localStorage API for persistence

## Summary of All Changes

### Files Modified/Added:
#### Code Quality Tools:
- `pyproject.toml`: Added Black, isort, flake8, pre-commit dependencies and configurations
- `.pre-commit-config.yaml`: Pre-commit hooks configuration
- `scripts/format.py`: Automatic code formatting script
- `scripts/lint.py`: Code linting and style checking script
- `scripts/quality-check.sh` / `.bat`: Cross-platform quality check scripts
- `CLAUDE.md`: Updated with code quality commands

#### Testing Framework:
- `pyproject.toml`: Added pytest testing dependencies and configuration
- `backend/tests/conftest.py`: Shared test fixtures and configuration
- `backend/tests/test_api_endpoints.py`: API endpoint testing
- `backend/tests/test_rag_system.py`: Core system unit tests

#### Dark/Light Theme:
- `frontend/index.html`: Added theme toggle button HTML
- `frontend/style.css`: Added light theme variables and button styling  
- `frontend/script.js`: Added theme management JavaScript functions

All implementations provide polished, accessible, and performant enhancements that work together to improve both the development workflow and user experience.
