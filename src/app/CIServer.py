from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import shutil
import tempfile
from git import Repo
import pylint.lint
from pylint.reporters import JSONReporter
from io import StringIO

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
            
            repo_url = payload['repository']['clone_url']
            branch = payload['ref'].split('/')[-1]  # refs/heads/branch-name -> branch-name
        
            result = clone_check(repo_url, branch) 
        
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'success', 'message': result}
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {'status': 'error', 'message': str(e)}
            self.wfile.write(json.dumps(error_response).encode())

def clone_check(repo_url, branch):
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"Cloning {repo_url} branch {branch} to {temp_dir}")
        repo = Repo.clone_from(repo_url, temp_dir, branch=branch)
        return syntax_check(temp_dir)
        
    except Exception as e:
        return f"Error during cloning: {str(e)}"
    finally:
        shutil.rmtree(temp_dir)

def syntax_check(directory):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    if not python_files:
        return "No Python files found to check"
    
    output = StringIO()
    reporter = JSONReporter(output)
    
    pylint_opts = [
        '--disable=all', 
        '--enable=syntax-error,undefined-variable', 
        *python_files
    ]
    
    try:
        pylint.lint.Run(pylint_opts, reporter=reporter, exit=False)
        result = output.getvalue()
        return "Syntax check passed" if not result.strip() else f"Syntax errors found: {result}"
    except Exception as e:
        return f"Error during syntax check: {str(e)}"


def run_server(port):
    server = HTTPServer(('', port), SimpleHandler)
    print(f'Server running on port {port}...')
    return server

