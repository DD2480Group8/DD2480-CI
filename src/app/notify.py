import requests
import subprocess

def set_commit_status(owner, repo, sha, token, state, description, target_url, context):
    """
    Update the commit status on GitHub.

    :param owner: GitHub username or organization name of the repository owner
    :param repo: Name of the repository
    :param sha: SHA-1 hash of the commit
    :param token: GitHub Personal Access Token
    :param state: State of the commit (can be "success", "failure", "error", "pending")
    :param description: Description of the commit status
    :param target_url: URL providing more details about the status (e.g., build or test results)
    :param context: The identifier for this status (e.g., "ci/build" or "ci/tests")
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/statuses/{sha}"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "state": state,
        "target_url": target_url,
        "description": description,
        "context": context
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("Commit status updated successfully!")
    else:
        print(f"Failed to update commit status: {response.status_code}")
        print(response.text)
