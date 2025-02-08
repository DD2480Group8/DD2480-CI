from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import shutil
import tempfile
from git import Repo
import pylint.lint
from pylint.reporters import JSONReporter
from notify import GithubNotification
from io import StringIO
from clone import clone_check
from syntax_check import syntax_check
from runTests import run_tests
from dotenv import load_dotenv
import stat
import errno

# Load environment variables from .env file
load_dotenv()


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        message = "Hello World!"
        self.wfile.write(message.encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data.decode('utf-8'))
            token = os.getenv('GITHUB_TOKEN')
            repo_url = payload['repository']['clone_url']
            gh = GithubNotification(payload['organization']['login'], payload['repository']['name'], token, "http://localhost:8008", "ci/tests")
            
            print(payload['ref'].split('/')[-2].lower())
            if payload['ref'].split('/')[-2].lower() == 'issue':
                branch = payload['ref'].split('/')[-2] + '/' + payload['ref'].split('/')[-1]
            else:
                branch = payload['ref'].split('/')[-1]  # refs/heads/branch-name -> branch-name
            result = clone_check(repo_url, branch) 
            test_results = run_tests(result)
            
            gh.send_commit_status("success", "Tests passed", payload['after'], "1") 

            if test_results:
                print("Tests Passed")
            else:
                print("One or more tests Failed")
                
            remove_temp_folder(result)
            token = os.getenv('GITHUB_TOKEN')
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'success', 'message': result, "test_results": test_results }
            # self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error: {str(e)}")
            gh.send_commit_status("failure", "Tests failed", payload['after'], "1")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {'status': 'error', 'message': str(e)}
            # self.wfile.write(json.dumps(error_response).encode())

def remove_temp_folder(folder):
    shutil.rmtree(folder, onerror=handle_remove_readonly)

def handle_remove_readonly(func, path, exc):
    # Change permissions to writeable if needed
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        # Ensure the item is writeable
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        func(path)  # Retry the removal
    else:
        raise excvalue

def run_server(port):
    server = HTTPServer(('', port), SimpleHandler)
    print(f'Server running on port {port}...')
    return server

