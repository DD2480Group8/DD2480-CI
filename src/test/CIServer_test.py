from io import StringIO
import json
import pytest
import requests
import threading
import time
import sys
from unittest.mock import Mock, patch
from app.syntax_check import syntax_check 
from app.notify import GithubNotification
from requests.exceptions import RequestException

from pathlib import Path
sys.path.extend([
    str(Path(__file__).parent.parent),
    str(Path(__file__).parent.parent / 'app')
])

from app.CIServer import process_webhook_payload

port = 8009


def test_do_POST_success():
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

    with patch('app.CIServer.clone_check', return_value=('commit_id_value', '/tmp/repo_path')), \
         patch('app.CIServer.syntax_check', return_value={
            "status": "success",
            "message": "Syntax check passed",
            "repository": {
                "url": "repo_url",
                "branch": "branch_name"
            },
            "files_checked": ['file1.py', 'file2.py'],
            "error_count": 0,
            "details": {}
         }), \
            patch('app.CIServer.run_tests', return_value=(True, "Test logs here")), \
            patch('app.CIServer.GithubNotification.send_commit_status') as mock_send_commit_status, \
            patch('app.CIServer.remove_temp_folder'):

        response = process_webhook_payload(payload, "1")
        assert response == True
        
        mock_send_commit_status.assert_called_with("success", "Tests passed", "commit_sha", "1")

def test_do_POST_clone_check_failure():
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

        response = process_webhook_payload(payload, "1")
        assert response == False
        mock_send_commit_status.assert_called_with("failure", "Clone failed", "commit_sha", "1")



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

def test_set_commit_status_success():
    """Test setting commit status to 'success' after passing syntax and tests"""
    
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
    
    with patch('app.CIServer.clone_check', return_value=('commitid', '/tmp/repo_path')), \
         patch('app.CIServer.syntax_check', return_value={
            "status": "success",
            "message": "Syntax check passed",
            "repository": {
                "url": "repo_url",
                "branch": "branch_name"
            },
            "files_checked": ['file1.py', 'file2.py'],
            "error_count": 0,
            "details": {}
        }), \
         patch('app.CIServer.run_tests', return_value=(True,"logs")), \
         patch('app.CIServer.GithubNotification.send_commit_status') as mock_send_commit_status, \
         patch('app.CIServer.remove_temp_folder'):

        response = process_webhook_payload(payload, "1")
        assert response == True
        
        # Verify if the send_commit_status function was called with 'success' status
        mock_send_commit_status.assert_called_with("success", "Tests passed", "commit_sha", "1")

def test_set_commit_status_test_failure():
    """Test setting commit status to 'failure' after failing tests"""
    
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
    
    with patch('app.CIServer.clone_check', return_value=('commitid', '/tmp/repo_path')), \
         patch('app.CIServer.syntax_check', return_value={
            "status": "success",
            "message": "Syntax check passed",
            "repository": {
                "url": "repo_url",
                "branch": "branch_name"
            },
            "files_checked": ['file1.py', 'file2.py'],
            "error_count": 0,
            "details": {}
         }), \
         patch('app.CIServer.run_tests', return_value=(False,"logs")), \
         patch('app.CIServer.GithubNotification.send_commit_status') as mock_send_commit_status, \
         patch('app.CIServer.remove_temp_folder'):

        response = process_webhook_payload(payload, "1")
        assert response == False
        
        # Verify if the send_commit_status function was called with 'failure' status due to test failure
        mock_send_commit_status.assert_called_with("failure", "Tests failed", "commit_sha", "1")

def test_notification_both_success():
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
    
    with patch('app.CIServer.clone_check', return_value=('commitid', '/tmp/repo_path')), \
         patch('app.CIServer.syntax_check', return_value={
            "status": "success",
            "message": "Syntax check passed",
            "repository": {
                "url": "repo_url",
                "branch": "branch_name"
            },
            "files_checked": ['file1.py', 'file2.py'],
            "error_count": 0,
            "details": {}
        }), \
         patch('app.CIServer.run_tests', return_value=(True,"logs")), \
         patch('app.CIServer.GithubNotification.send_commit_status') as mock_send_status, \
         patch('app.CIServer.remove_temp_folder'):
        
        response = process_webhook_payload(payload, "1")
        assert response == True
        
        calls = mock_send_status.call_args_list
        assert len(calls) == 4
        assert any(call[0][0] == "pending" and "syntax" in call[0][1].lower() for call in calls)
        assert any(call[0][0] == "pending" and "test" in call[0][1].lower() for call in calls)
        assert any(call[0][0] == "success" and "syntax" in call[0][1].lower() for call in calls)
        assert any(call[0][0] == "success" and "test" in call[0][1].lower() for call in calls)

def test_notification_syntax_failure():
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
    
    with patch('app.CIServer.clone_check', return_value=('commitid', '/tmp/repo_path')), \
         patch('app.CIServer.syntax_check', return_value={
                "status": "error",
                "message": "Syntax errors found",
                "repository": {
                    "url": "repo_url",
                    "branch": "branch_name"
                },
                "files_checked": ['file1.py', 'file2.py'],
                "error_count": 1,
                "details": ['error']
            }), \
         patch('app.CIServer.run_tests', return_value=(True,"logs")), \
         patch('app.CIServer.GithubNotification.send_commit_status') as mock_send_status, \
         patch('app.CIServer.remove_temp_folder'):
        
        response = process_webhook_payload(payload, "1")
        assert response == False
        
        calls = mock_send_status.call_args_list
        assert len(calls) == 4
        assert any(call[0][0] == "pending" and "syntax" in call[0][1].lower() for call in calls)
        assert any(call[0][0] == "pending" and "test" in call[0][1].lower() for call in calls)
        assert any(call[0][0] == "failure" and "syntax check failed" in call[0][1].lower() for call in calls)
        assert any(call[0][0] == "error" and "tests cannot be run due to failing the syntax check" in call[0][1].lower() for call in calls)

def test_notification_network_error():
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
         patch('app.CIServer.syntax_check', return_value={
            "status": "success",
            "message": "Syntax check passed",
            "repository": {
                "url": "repo_url",
                "branch": "branch_name"
            },
            "files_checked": ['file1.py', 'file2.py'],
            "error_count": 0,
            "details": {}
        }), \
         patch('app.CIServer.run_tests', return_value=(True,"logs")), \
         patch('app.CIServer.GithubNotification.send_commit_status', side_effect=RequestException("Network error")), \
         patch('app.CIServer.remove_temp_folder'):
        
        try:
            response = process_webhook_payload(payload, "1")
            assert response == False
        except requests.exceptions.ConnectionError:
            pytest.fail("Server connection failed")

def test_notification_invalid_repo():
    payload = {
        "repository": {
            "clone_url": "https://github.com/invalid/repo.git",
            "name": "invalid-repo"
        },
        "ref": "refs/heads/main",
        "organization": {
            "login": "invalid-org"
        },
        "after": "commit_sha"
    }
    
    with patch('app.CIServer.clone_check', side_effect=Exception("Invalid repository")), \
         patch('app.CIServer.GithubNotification.send_commit_status') as mock_send_status:
        
        response = process_webhook_payload(payload, "1")
        assert response == False
        mock_send_status.assert_called_with("failure", "Clone failed", "commit_sha", "1")
