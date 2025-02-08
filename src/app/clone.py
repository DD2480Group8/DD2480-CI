import tempfile
import shutil
from git import Repo
import os
from syntax_check import syntax_check
import uuid

PROJ_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP_PATH = os.path.abspath(os.path.join(PROJ_ROOT, "tmp/"))

def ensure_tmp_directory():
    """
    Ensures that the tmp directory exists.
    Creates it if it doesn't exist, with proper permissions.
    """
    try:
        if not os.path.exists(TMP_PATH):
            os.makedirs(TMP_PATH, mode=0o755)  # rwxr-xr-x permissions
            print(f"Created tmp directory at {TMP_PATH}")
    except Exception as e:
        print(f"Error creating tmp directory: {str(e)}")
        raise

def cleanup_tmp_directory():
    """
    Cleans up old temporary directories in the tmp folder.
    """
    if os.path.exists(TMP_PATH):
        try:
            shutil.rmtree(TMP_PATH)
            os.makedirs(TMP_PATH, mode=0o755)
            print("Cleaned up tmp directory")
        except Exception as e:
            print(f"Error cleaning up tmp directory: {str(e)}")
            raise

def clone_check(repo_url, branch):
    try:
        # Ensure tmp directory exists
        ensure_tmp_directory()
        
        # Create a unique directory for this clone
        temp_dir = os.path.join(TMP_PATH, str(uuid.uuid4()))
        os.makedirs(temp_dir, mode=0o755)  # Create with proper permissions
        
        print(f"Cloning {repo_url} branch {branch} to {temp_dir}")
        repo = Repo.clone_from(repo_url, temp_dir, branch=branch)
        
        result = syntax_check(temp_dir)
      
        return temp_dir
        
    except Exception as e:
        # Clean up temp_dir if it was created
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            
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