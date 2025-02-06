import pytest
import requests
import threading
import time
import sys
from pathlib import Path
sys.path.extend([
    str(Path(__file__).parent.parent),
    str(Path(__file__).parent.parent / 'app')
])

from app.CIServer import run_server
from app.clone import clone_check
from http.server import HTTPServer, BaseHTTPRequestHandler
from app.CIServer import SimpleHandler

@pytest.fixture(scope="module")
def server():
    """Start the server in a separate thread"""
    port = 8088
    server = run_server(port)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    time.sleep(1)
    
    yield f"http://localhost:{port}"
    
    # Cleanup
    server.shutdown()
    server.server_close()
    thread.join()

def test_valid_post_request(server):
    """Test valid webhook POST request"""

    mock_payload = {
        "repository": {"clone_url": "https://github.com/FMurkz/DD2480-CI.git"},
        "ref": "refs/heads/main"
    }
    
    response = requests.post(f"{server}/", json=mock_payload)  

    assert response.status_code == 200


def test_invalid_post_request(server):
    """Test invalid webhook POST request"""

    mock_payload = {
        "repository": {"clone_url": "https://github.com/FMurkz/DD2480-CI.git"}
    }
    
    response = requests.post(f"{server}/github-webhook/", json=mock_payload)
    
    assert response.status_code == 500
    
    data = response.json()
    
    assert data["status"] == "error" 
    assert "message" in data
    assert "ref" in data["message"]


def test_clone_check_valid_request():
    """Test valid clone_check request"""

    repo_url = "https://github.com/FMurkz/DD2480-CI.git"
    branch = "main"

    result = clone_check(repo_url, branch)

    assert result["status"] == "success"
    assert "message" in result
    assert result["repository"]["url"] == repo_url
    assert result["repository"]["branch"] == branch


def test_clone_check_invalid_request():
    """Test invalid clone_check request"""

    repo_url = "https://github.com/invalid/repo.git"  
    branch = "main"

    result = clone_check(repo_url, branch)

    assert result["status"] == "error"
    assert "message" in result
    assert "Error during cloning" in result["message"]
    