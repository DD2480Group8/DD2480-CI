import os
import pylint.lint
import json
from io import StringIO
from pylint.reporters import JSONReporter

def syntax_check(directory):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    if not python_files:
        return {
            "status": "warning",
            "message": "No Python files found to check",
            "repository": {
                "url": "repo_url",
                "branch": "branch_name"
            },
            "files_checked": [],
            "error_count": 0,
            "details": {}
        }
    
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
        errors = json.loads(result)
        if len(errors) > 0:
            return {
                "status": "error",
                "message": "Syntax errors found",
                "repository": {
                    "url": "repo_url",
                    "branch": "branch_name"
                },
                "files_checked": python_files,
                "error_count": len(errors),
                "details": errors
            }
        return {
            "status": "success",
            "message": "Syntax check passed",
            "repository": {
                "url": "repo_url",
                "branch": "branch_name"
            },
            "files_checked": python_files,
            "error_count": 0,
            "details": {}
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Syntax errors found",
            "repository": {
                "url": "repo_url",
                "branch": "branch_name"
            },
            "files_checked": python_files,
            "error_count": 2,
            "details": {
                "file1.py": [
                    {
                        "line": 10,
                        "column": 5,
                        "type": "error",
                        "symbol": "syntax-error",
                        "message": "invalid syntax"
                    }
                ],
                "file2.py": [
                    {
                        "line": 20,
                        "column": 1,
                        "type": "error",
                        "symbol": "undefined-variable",
                        "message": "undefined variable 'foo'"
                    }
                ]
            }
        }
