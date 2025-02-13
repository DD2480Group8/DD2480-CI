# DD2480-CI

## Overview
This project implements a basic Continuous Integration (CI) server that automates key development tasks. When a developer pushes code changes to a GitHub repository, GitHub sends a webhook notification to the CI server. The server retrieves repository details from the webhook payload, clones the repository, and checks out the updated branch. It then performs a syntax check using Pylint, followed by executing unit tests with pytest. Based on the test results, the CI server updates the commit status on GitHub and sends notifications about the build outcome via the configured method.

## Project Structure
```
DD2480-CI/
├── src/
│   ├── app/                    # Main application code
│   │   ├── CIServer.py        # Core CI server implementation
│   │   ├── clone.py           # Repository cloning functionality
│   │   ├── notify.py          # GitHub status notification system
│   │   ├── runTests.py        # Test execution handler
│   │   ├── syntax_check.py    # Python syntax validation
│   │   ├── build_history.py    # Create database
│   │   └── main.py           # Server entry point
│   └── test/                  # Test suite
│       ├── test_build_history.py    # Tests for database
│       └── CIServer_test.py   # Comprehensive tests for CI server
```

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


## Setup - Not using docker
Install Python 3.13.1 and pip 24.3.1

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
    .\venv\Scripts\activate
    ```
    
    In the virutal environment run the following command to install all necessary dependencies_

    ```pip install -r requirements.txt```

    - Use command ```deactivate``` to close environment
3. Create a Github personal access token
4. Add .env file to Root directory of the project
    - Add the following line to the .env file:

    ```GITHUB_TOKEN=your personal access token here```
## Expose your local host
1. Open ngrok tunnel
    ```ngrok http http://localhost:8008```
    - OBS! port needs to be 8008
2. Add the ngrok URL to a github webhook that can recieve push events


## Running the program

1. To run server, use following command:

```bash
python src/app/main.py
```

2. To run tests run the following command:
```bash
pytest src/test/CIServer_test.py
```

## Run Server with docker image
### Build the container
```bash
docker build . -t {nameofimage}
```
### Running server
```bash
docker run -e GITHUB_TOKEN={your_github_token_here} -p 8008:8008 {name of image}
```
## Running pydoc
1. Make sure you can run the ```pydoc``` command, if not, Install ```pydoc```
2. cd into the src folder running this command:
 ```bash
 cd src
 ```

 3. get pydocs for the files in app:
 ```bash
 pydoc app/{filename}.py
 ```

 4. get pydocs for the files in test:
 ```bash
 pydoc test/{filename}.py
 ```


## Statement of contributions

### Felicia Murkes:
- Setup HTTP server
- Setup docker image
- Bugfixes on all three core features
- Connected all features
- Made some tests for do_post, clonechecker and syntax check
- Some fixes to broken tests
- Added two get endpoints to view the log history
- Added queue to prevent timeout
- Added logging

### Eyüp Ahmet Başaran
- Implemented core feature 1
- Fixes related to tmp directory management
- Notification tests

### Bingjie Zhao
- Implemented core feature three
- Tests for notify() function
- fixed bugs in CIServer related to commit status;

### Ismail 
- Implemeted database
- Tests for syntax check
- Implemented test cases for database
- database bug fixes

### Melissa Saber
- Implemented core feature 2
- wrote documatation for functions


## How we used github
We used some prefixes for the commits so that we easily could see what each commit did

- feat: a new implementation was made
- test: testcase was written for a function or for the program
- refactor: The code was changed in some way without implementing something new
- fix: a bug was fixed
- doc: documentation was added
- setup: for any comits related to setup
- deploy: any commits related to deployment of server 

These were the steps we took once an issue was created and a group member was assigned to it

1. A branch was created and named after the issue
2. All the commits needed were committed
    - All commits has a prefix
    - All commits reference the issue by adding (#xx) at the end, xx being the issue number
5. Once the issue has been fixed a pull request was made to merge it into main
6. Any merge conflicts were handled
7. Lastly it was merged into main

## Our way of working, SEMAT
We began this project by analyzing the problem and familiarizing ourselves with the environment. Based on our skills and the needs of the
project, we decided to use Python as the programming language and VSCode as the primary development tool. The principles of our way of
working were established, focusing on creating a smooth, automated CI pipeline. We integrated GitHub for version control and ngrok to
expose the local server, setting up a webhook that allowed us to automate repository cloning, syntax checks, and testing. The project
structure was outlined, with initial practices like task management using GitHub issues, ensuring each task was tracked, and every commit
was linked to a specific task. As we progressed, the team started using the tools and practices consistently, with everyone becoming
comfortable with GitHub and ngrok, enabling efficient collaboration and communication. In the “In Place” phase, the entire team had
integrated these practices and tools into their daily workflow. Everyone had access to the tools required to complete their tasks, and
the practices were being used by the whole team. We continuously adapted our approach as necessary, ensuring that the CI pipeline
functioned smoothly and was aligned with the evolving project needs. We didn’t reach the “Working Well” phase yet, as some practices
still required refinement, but we are confident that the strong foundation we’ve established will allow us to continuously improve and
reach that stage in the future.