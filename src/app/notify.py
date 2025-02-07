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

def notify_commit_status(result):
    """
    Set the GitHub commit status based on the test results.
    
    :param result: The result object containing the return code and output information from the test
    """
    owner = "DD2480Group8"
    repo = "DD2480-CI"
    
    # Get the current commit SHA-1 hash
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode("utf-8")
    
    token = "personal_access_token"  #GitHub Personal Access Token
    
    # Set state and description based on the test result
    if result.returncode == 0:
        state = "success"
        description = "Tests passed"
    else:
        state = "failure"
        description = f"Tests failed: {result.stdout}"
    
    target_url = "http://example.com/test/results"  # Replace with your test results URL
    context = "ci/tests"  # Typically "ci/build" or "ci/tests" to indicate the status context
    
    set_commit_status(
        owner=owner,
        repo=repo,
        sha=sha,
        token=token,
        state=state,
        description=description,
        target_url=target_url,
        context=context
    )

# # Example: Run tests and notify GitHub with the status
# if __name__ == "__main__":
#     result = subprocess.run(["pytest", "--tb=short", "test/"], capture_output=True, text=True)
#     notify_commit_status(result)