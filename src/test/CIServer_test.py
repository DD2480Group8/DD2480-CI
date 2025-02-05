import pytest
import requests
import threading
import time
from app.CIServer import run_server
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
    
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data


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

