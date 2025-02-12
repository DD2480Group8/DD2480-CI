# DD2480-CI
## Overview
## Project Structure
## Key Components

**CI Server (CIServer.py)**
- Core server implementation handling webhook requests from GitHub
- Orchestrates the entire CI pipeline including cloning, syntax checking, and test execution
- Manages GitHub status updates for each stage of the pipeline

**Repository Management (clone.py)**
- Handles secure cloning of repositories
- Creates and manages temporary directories for repository processing
- Ensures proper cleanup after CI operations

**Notification System (notify.py)**
- Implements GitHub status API integration
- Updates commit statuses for syntax checks and test results
- Provides real-time feedback on CI pipeline stages

**Code Quality Tools**
- Syntax Checker (syntax_check.py)
- Performs Python syntax validation using Pylint
- Identifies syntax errors and undefined variables
- Generates detailed error reports

**Test Runner (runTests.py)**
- Executes pytest-based test suites
- Reports test results back to the CI pipeline

**Testing Framework**
- Comprehensive test suite covering all major components
- Includes mocked tests for GitHub interactions
- Tests for success and failure scenarios of the CI pipeline
- Network error handling and edge case coverage

## Setup

Install Python 3.13.1

1. When you have installed python, Use the following command to create a virtual environment:

```bash
python3 -m venv venv
```

2. To enter virtual environment

    To enter virtual environment (For MacOS), run:

    ```bash
    source venv/bin/activate
    ```

    To enter virtual environment (For Windows), run:

    ```bash
    ./venv/bin/activate
    ```

    - Use command ```deactivate``` to close environment

## Running the program

1. To run server, use following command:

```bash
python src/app/CIServer.py
```

2. To run tests run the following command:
```bash
pytest src/test/CIServer_test.py
```


## Statement of contributions

## How we used git
## Our way of working (SEMAT)
