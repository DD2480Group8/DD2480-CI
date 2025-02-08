import pytest
import requests
import threading
import time
import sys
from unittest.mock import patch

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



