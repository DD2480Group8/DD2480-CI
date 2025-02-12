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
        """Handles GET requests by responding with a simple message."""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        message = "Hello World!"
        self.wfile.write(message.encode())

    def do_POST(self):
        """
        Handles POST requests from GitHub webhooks.

        Extracts repository and branch details from the payload, Clones the repository.
        Runs a syntax check using Pylint, Executes tests.
        Updates the commit status on GitHub and sends a JSON response with the results.

        Raises:
            Exception: If syntax check or tests fail, GitHub commit status is updated accordingly.
        """
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data.decode('utf-8'))
            token = os.getenv('GITHUB_TOKEN')
            repo_url = payload['repository']['clone_url']
            ghSyntax = GithubNotification(payload['organization']['login'], payload['repository']['name'], token, "http://localhost:8008", "ci/syntaxcheck")
            ghTest = GithubNotification(payload['organization']['login'], payload['repository']['name'], token, "http://localhost:8008", "ci/tests")
            
            print(payload['ref'].split('/')[-2].lower())
            if payload['ref'].split('/')[-2].lower() == 'issue':
                branch = payload['ref'].split('/')[-2] + '/' + payload['ref'].split('/')[-1]
            else:
                branch = payload['ref'].split('/')[-1]  # refs/heads/branch-name -> branch-name
            
            try:
                result = clone_check(repo_url, branch)
            except Exception as clone_error:
                print(f"Error: {str(clone_error)}")
                try:
                    ghTest.send_commit_status("failure", "Tests failed", payload['after'], "1")
                except Exception as notify_error:
                    if "Network error" in str(notify_error):
                        print(f"Warning: Failed to send notification: {str(notify_error)}")
                raise clone_error

            syntaxcheck = syntax_check(result)
            
            try:
                if syntaxcheck:
                    print("Syntax Check Passed")
                    ghSyntax.send_commit_status("success", "Syntax check passed", payload['after'], "1") 
                else:
                    print("Syntax Check Failed")
                    ghSyntax.send_commit_status("failure", "Syntax check failed", payload['after'], "1")
                    raise Exception("Syntax check failed")
            except Exception as notify_error:
                if "Network error" in str(notify_error):
                    print(f"Warning: Failed to send notification: {str(notify_error)}")
                else:
                    raise notify_error

            if not syntaxcheck:
                raise Exception("Syntax check failed")

            test_results = run_tests(result)
            try:
                if test_results:
                    print("Test Passed")
                    ghTest.send_commit_status("success", "Tests passed", payload['after'], "1") 
                else:
                    print("Test Failed")
                    ghTest.send_commit_status("failure", "Tests failed", payload['after'], "1")
            except Exception as notify_error:
                if "Network error" in str(notify_error):
                    print(f"Warning: Failed to send notification: {str(notify_error)}")
                else:
                    raise notify_error

            if not test_results:
                raise Exception("Tests failed")

            remove_temp_folder(result)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'success', 'message': result, "test_results": test_results }
            
        except Exception as e:
            print(f"Error: {str(e)}")
            try:
                if "Syntax check failed" in str(e):
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    error_response = {'status': 'error', 'message': str(e)}
                else:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    error_response = {'status': 'error', 'message': str(e)}
            except Exception as send_error:
                print(f"Error sending response: {str(send_error)}")

def remove_temp_folder(folder):
    """
    Removes a temporary folder.

    Args:
        folder (str): Path of the directory to be removed.
    """
    shutil.rmtree(folder, onerror=handle_remove_readonly)

def handle_remove_readonly(func, path, exc):
    """
    Handles removal of read-only files by modifying permissions.

    Args:
        func: Function that triggered the error
        path: File path causing the issue
        exc: Exception details
    """
    # Change permissions to writeable if needed
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        # Ensure the item is writeable
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        func(path)  # Retry the removal
    else:
        raise excvalue

def run_server(port):
    """
    Starts an HTTP server on the specified port.

    Args:
        port: Port number for the server

    Returns:
        HTTPServer: The running server instance.
    """
    server = HTTPServer(('', port), SimpleHandler)
    print(f'Server running on port {port}...')
    return server

