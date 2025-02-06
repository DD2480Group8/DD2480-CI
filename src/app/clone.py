import tempfile
import shutil
from git import Repo
from syntax_check import syntax_check

def clone_check(repo_url, branch):
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"Cloning {repo_url} branch {branch} to {temp_dir}")
        repo = Repo.clone_from(repo_url, temp_dir, branch=branch)
        
        result = syntax_check(temp_dir)
        result["repository"] = {
            "url": repo_url,
            "branch": branch
        }
        return result
        
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
    finally:
        shutil.rmtree(temp_dir)