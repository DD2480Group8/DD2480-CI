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
    thread.daemon = True  # Daemon threads are abruptly stopped when program exits
    thread.start()
    
    # Give the server a moment to start
    time.sleep(1)
    
    yield f"http://localhost:{port}"
    
    # Cleanup
    server.shutdown()
    server.server_close()
    thread.join()

def test_webhook_endpoint(server):
    """Test the webhook endpoint"""
    response = requests.post(f"{server}")
    assert response.status_code == 200
    data = response.text
    assert data == 'Webhook received'
