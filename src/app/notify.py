import requests
import subprocess


class GithubNotification:
    def __init__(self, owner, repo, token, target_url, context):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.target_url = target_url
        self.context = context
        
    def send_commit_status(self, state, description, sha, run_id):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/statuses/{sha}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "state": state,
            "target_url": f"{self.target_url}/{run_id}",
            "description": description,
            "context": self.context
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            print("Commit status updated successfully!")
        except requests.exceptions.RequestException as e:
            print(f"Failed to update commit status: {e}")
            print(response.text)