from io import StringIO
import json
import pytest
import requests
import threading
import time
import sys
from unittest.mock import Mock, patch
from app.syntax_check import syntax_check 

from pathlib import Path
sys.path.extend([
    str(Path(__file__).parent.parent),
    str(Path(__file__).parent.parent / 'app')
])

from app.CIServer import run_server
from app.clone import clone_check
from http.server import HTTPServer, BaseHTTPRequestHandler
from app.CIServer import SimpleHandler

port = 8009

@pytest.fixture
def start_server():
    server = HTTPServer(('localhost', port), SimpleHandler)
    threading.Thread(target=server.serve_forever).start()
    time.sleep(1)
    yield
    server.shutdown()
    server.server_close()

def test_do_POST_success(start_server):
    """Test the do_POST method for a successful flow"""
    payload = {
        "repository": {
            "clone_url": "https://github.com/DD2480Group8/DD2480-CI.git",
            "name": "DD2480-CI"
        },
        "ref": "refs/heads/main",
        "organization": {
            "login": "DD2480Group8"
            
        },
        "after": "commit_sha"
    }

    with patch('app.CIServer.clone_check', return_value='/tmp/repo_path'), \
            patch('app.CIServer.syntax_check', return_value=True), \
            patch('app.CIServer.run_tests', return_value=True), \
            patch('app.CIServer.GithubNotification.send_commit_status') as mock_send_commit_status, \
            patch('app.CIServer.remove_temp_folder'):

        response = requests.post(f"http://localhost:{port}/", json=payload)
        assert response.status_code == 200
        mock_send_commit_status.assert_called_with("success", "Tests passed", "commit_sha", "1")

def test_do_POST_clone_check_failure(start_server):
    """Test the do_POST method for a failure flow in clone_check"""
    payload = {
        "repository": {
            "clone_url": "https://github.com/DD2480Group8/DD2480-CI.git",
            "name": "DD2480-CI"
        },
        "ref": "refs/heads/main",
        "organization": {
            "login": "DD2480Group8"
        },
        "after": "commit_sha"
    }

    with patch('app.CIServer.clone_check', side_effect=Exception("Clone failed")), \
            patch('app.CIServer.GithubNotification.send_commit_status') as mock_send_commit_status:

        response = requests.post(f"http://localhost:{port}/", json=payload)
        assert response.status_code == 500
        mock_send_commit_status.assert_called_with("failure", "Tests failed", "commit_sha", "1")



def test_syntax_check_success():
    """Test the syntax_check function for a successful syntax check"""
    mock_directory = '/tmp/test_repo'

    with patch('os.walk') as mock_walk, \
         patch('pylint.lint.Run') as mock_run, \
         patch('app.syntax_check.StringIO') as mock_stringio:

        mock_walk.return_value = [(mock_directory, ['subdir'], ['file1.py', 'file2.py'])]
        mock_output = Mock()
        mock_output.getvalue.return_value = '[]'
        mock_stringio.return_value = mock_output

        result = syntax_check(mock_directory)

        assert result["status"] == "success"
        assert result["error_count"] == 0
        assert len(result["files_checked"]) == 2  


def test_syntax_check_failure():
    """Test the syntax_check function for a failed syntax check"""
    mock_directory = '/tmp/test_repo'

    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            (mock_directory, ['subdir'], ['file1.py', 'file2.py'])
        ]
    
        with patch('pylint.lint.Run', side_effect=Exception("Syntax error encountered")) as mock_pylint_run:
           
            result = syntax_check(mock_directory)                     
            assert result["status"] == "error"  
            assert "Syntax errors found" in str(result["message"])

def test_syntax_check_warning():
    """Test the syntax_check function for the warning case when no Python files are found"""
    
    mock_directory = '/tmp/test_repo'
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            (mock_directory, ['subdir'], ['file1.txt', 'file2.md'])
        ]
        result = syntax_check(mock_directory)
        assert result["status"] == "warning"
        assert "No Python files found to check" in result["message"]

def test_syntax_check_at_least_one_error_found():
    """Test the syntax_check function for the case when at least one error is found"""
    mock_directory = '/tmp/test_repo'
    with patch('os.walk') as mock_walk, \
         patch('pylint.lint.Run') as mock_run, \
         patch('app.syntax_check.StringIO') as mock_stringio:
        mock_walk.return_value = [(mock_directory, ['subdir'], ['file1.py', 'file2.py'])]
        mock_output = Mock()
        mock_output.getvalue.return_value = '[{"path": "file1.py", "line": 1, "column": 1, "message": "Syntax errors found"}]'
        mock_stringio.return_value = mock_output

        result = syntax_check(mock_directory)
        assert result["status"] == "error"
        assert result["error_count"] == 1
        assert len(result["files_checked"]) == 2
        assert "Syntax errors found" in result["message"]
