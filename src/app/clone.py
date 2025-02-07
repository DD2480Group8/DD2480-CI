import tempfile
import shutil
from git import Repo
import os
from syntax_check import syntax_check
import uuid
PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_PATH = os.path.abspath(os.path.join(PROJ_ROOT, "tmp/"))

def clone_check(repo_url, branch):

    try:
        temp_dir = os.path.join(TMP_PATH, str(uuid.uuid4()))
        os.mkdir(temp_dir)
        print(f"Cloning {repo_url} branch {branch} to {temp_dir}")
        repo = Repo.clone_from(repo_url, temp_dir, branch=branch)
        
        result = syntax_check(temp_dir)
      
        return temp_dir
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error during cloning: {str(e)}",
            "repository": {
                "url": repo_url,
                "branch": branch
            },
            "error_count": -1,
            "details": {"error": str(e)}
        }