from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import shutil
import tempfile
import uuid
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
import re
from build_history import get_highest_log_id, log_build, get_github_commit_url, create_database, get_logs, get_log
from queue import Queue
import threading

create_database()
# Load environment variables from .env file
load_dotenv()

task_queue = Queue()

def process_queue():
    """
    Worker function that processes tasks from the queue continuously.
    """
    while True:
        task = task_queue.get()
        if task is None:
            break
        
        payload, build_id = task
        try:
            log_id = get_highest_log_id() + 1
            process_webhook_payload(payload, log_id)
        except Exception as e:
            print(f"Error processing task {build_id}: {str(e)}")
        finally:
            task_queue.task_done()

def process_webhook_payload(payload,log_id):
    """
        Processes a webhook payload from GitHub, performing syntax checks and running tests on the specified repository.
        Args:
            payload (dict): The webhook payload from GitHub containing repository and commit information.
            log_id (str): The unique identifier for the log entry.
        Returns:
            bool: True if the process completes successfully, False otherwise.
        Raises:
            Exception: If there are errors during cloning, syntax checking, or testing.
        
    """
    try:
            token = os.getenv('GITHUB_TOKEN')
            repo_url = payload['repository']['clone_url']
            commit_id = payload['after']
            ghSyntax = GithubNotification(payload['organization']['login'], payload['repository']['name'], token, "http://localhost:8008", "ci/syntaxcheck")
            ghTest = GithubNotification(payload['organization']['login'], payload['repository']['name'], token, "http://localhost:8008", "ci/tests")
            
            
            if payload['ref'].split('/')[-2].lower() == 'issue':
                branch = payload['ref'].split('/')[-2] + '/' + payload['ref'].split('/')[-1]
            else:
                branch = payload['ref'].split('/')[-1]  # refs/heads/branch-name -> branch-name
            try:
                # Send a pending status notification to GitHub
                ghSyntax.send_commit_status("pending", "Running syntax check", payload['after'], log_id)
                ghTest.send_commit_status("pending", "Running tests", payload['after'], log_id)
            except Exception as notify_error:
                if "Network error" in str(notify_error):
                    print(f"Warning: Failed to send notification: {str(notify_error)}")
                raise notify_error
            
            try:
                commit_id, result = clone_check(repo_url, branch)
            except Exception as clone_error:
                print(f"Error: {str(clone_error)}")
                try:
                    ghTest.send_commit_status("failure", "Clone failed", payload['after'], log_id)
                    ghSyntax.send_commit_status("failure", "Clone failed", payload['after'], log_id)
                except Exception as notify_error:
                    if "Network error" in str(notify_error):
                        print(f"Warning: Failed to send notification: {str(notify_error)}")
                raise clone_error

            syntaxcheck = syntax_check(result)
            
            try:
                if syntaxcheck['status'] == "success":
                    print("Syntax Check Passed")
                    ghSyntax.send_commit_status("success", "Syntax check passed", payload['after'], log_id) 
                else:
                    print("Syntax Check Failed")
                    ghSyntax.send_commit_status("failure", "Syntax check failed", payload['after'], log_id)
            except Exception as notify_error:
                if "Network error" in str(notify_error):
                    print(f"Warning: Failed to send notification: {str(notify_error)}")
                else:
                    raise notify_error

            if syntaxcheck['status'] == "error":
                ghTest.send_commit_status("error", "Tests cannot be run due to failing the syntax check", payload['after'], log_id)
                raise Exception("Syntax check failed")

            test_results, test_logs = run_tests(result)
            try:
                if test_results:
                    print("Test Passed")
                    ghTest.send_commit_status("success", "Tests passed", payload['after'], log_id) 
                else:
                    print("Test Failed")
                    ghTest.send_commit_status("failure", "Tests failed", payload['after'], log_id)
            except Exception as notify_error:
                if "Network error" in str(notify_error):
                    print(f"Warning: Failed to send notification: {str(notify_error)}")
                else:
                    raise notify_error

            if not test_results:
                raise Exception("Tests failed")


            if not commit_id:   
                raise Exception("Error cloning repository.")
            
            
            return True
            
    except Exception as e:
        return False
    finally:
        log_parts = []

        # Add Log ID if it exists
        if 'log_id' in locals() or 'log_id' in globals():
            log_parts.append(f"Log ID: {log_id}")

        # Add Commit ID if it exists
        if 'commit_id' in locals() or 'commit_id' in globals():
            log_parts.append(f"Commit ID: {commit_id}")

        # Add Syntax Check if both json and syntaxcheck exist
        if ('json' in locals() or 'json' in globals()) and ('syntaxcheck' in locals() or 'syntaxcheck' in globals()):
            log_parts.append("\nSyntax Check:\n=================")
            log_parts.append(json.dumps(syntaxcheck, indent=4))
            log_parts.append("=================")

        # Add Test Results if test_logs exists
        if 'test_logs' in locals() or 'test_logs' in globals():
            log_parts.append("\nTest Results:\n=================")
            log_parts.append(test_logs)
            log_parts.append("=================")
        
        log_build(commit_id, "".join(log_parts))  # Log the build results                     

        if 'result' in locals() or 'result' in globals():
            remove_temp_folder(result)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
        Handle GET requests to the server for getting build logs
        """
        # Parse the requested path
        path = self.path
        field_names = ["id", "commit_id", "build_date", "build_logs", "github_commit_url"]

        
        if path == "/":
            # Handle the root path
            self.send_response(200)
            self.send_header('Content-type', 'application/json')

            self.end_headers()
            message = get_logs()
            data = [dict(zip(field_names, item)) for item in message]
            self.wfile.write(json.dumps(data).encode())
        
        elif re.match(r"^/\d+$", path):  # Check if the path matches "/{id}" where id is a number
            # Extract the ID from the path
            id_value = path[1:]  # Remove the leading '/'
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = get_log(id_value)
            data = dict(zip(field_names, message))
            self.wfile.write(json.dumps(data).encode())
        
        else:
            # Handle unknown paths
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = "404 Not Found"
            self.wfile.write(message.encode())

    def do_POST(self):
        """
        Handles POST requests from GitHub webhooks by queueing them for background processing.
        Immediately returns a 202 Accepted response.
        """
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data.decode('utf-8'))
            build_id = str(uuid.uuid4())
            
            # Queue the task for background processing
            task_queue.put((payload, build_id))
            
            # Immediately return success response
            self.send_response(202)  # 202 Accepted
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'accepted',
                'message': 'Build queued for processing',
                'build_id': build_id
            }
            self.wfile.write(json.dumps(response).encode())
            
        except json.JSONDecodeError as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {'status': 'error', 'message': 'Invalid JSON payload'}
            self.wfile.write(json.dumps(error_response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(error_response).encode())

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
    Starts an HTTP server on the specified port with a background worker thread.
    """
    # Start the worker thread
    worker_thread = threading.Thread(target=process_queue, daemon=True)
    worker_thread.start()
    
    server = HTTPServer(('', port), SimpleHandler)
    print(f'Server running on port {port}...')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        # Signal the worker thread to stop
        task_queue.put(None)
        worker_thread.join()
        server.server_close()