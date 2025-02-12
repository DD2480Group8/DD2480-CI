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
    Ensures the existence of the temporary directory used for cloning repositories.

    Creates the directory at TMP_PATH if it does not exist and sets permissions to 755.
    Prints a message when the directory is created.

    Raises:
        Exception: If an error occurs while creating the directory.
    """
    try:
        if not os.path.exists(TMP_PATH):
            os.makedirs(TMP_PATH, mode=0o755)
            print(f"Created tmp directory at {TMP_PATH}")
    except Exception as e:
        print(f"Error creating tmp directory: {str(e)}")
        raise



def clone_check(repo_url, branch):
    """
    Clones a Git repository to a temporary directory and returns the directory path.

    Args:
        repo_url (str): URL of the Git repository to clone.
        branch (str): The branch to clone.

    Returns:
        str: Path to the cloned repository if successful.
        dict: Error details if cloning fails.

    Raises:
        Exception: If an error occurs during cloning, the function cleans up and returns an error dictionary.
    """
    try:
        ensure_tmp_directory()
        temp_dir = os.path.join(TMP_PATH, str(uuid.uuid4()))
        os.makedirs(temp_dir, mode=0o755)
        
        print(f"Cloning {repo_url} branch {branch} to {temp_dir}")
        repo = Repo.clone_from(repo_url, temp_dir, branch=branch)
        commit_id = repo.head.commit.hexsha      
        return commit_id, temp_dir
        
    except Exception as e:
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