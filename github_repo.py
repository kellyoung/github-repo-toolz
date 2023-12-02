import json
import requests


class GitHubRepo:
    """
    Represents a GitHub repository and provides methods to interact with its API.
    """

    BASE_URL = "https://api.github.com/repos"

    def __init__(self, owner: str, repo: str, token: str):
        """
        Initialize a GitHubRepo instance.

        Parameters:
        - owner (str): The owner or organization of the repository.
        - repo (str): The name of the repository.
        - token (str): Personal access token for authentication.
        """
        self.owner = owner
        self.repo = repo
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.base_url = f"{GitHubRepo.BASE_URL}/{owner}/{repo}"

    def _make_request(self, method: str, endpoint: str, data=None):
        """
        Make an authenticated request to the GitHub API.

        Parameters:
        - method (str): HTTP method for the request (e.g.'GET','POST','PATCH').
        - endpoint (str): The API endpoint for the request.
        - data (dict): Optional data to include in the request payload.

        Returns:
        dict:
        - data: The JSON response from the API.
        - status_code: the HTTP status code of the response from the API
        """
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(
            method, url, headers=self.headers, data=json.dumps(data)
        )
        response.raise_for_status()

        return {"data": response.json(), "status_code": response.status_code}

    def get_latest_commit_sha(self, branch: str = "main"):
        """
        Get the SHA of the latest commit on a specific branch.

        Parameters:
        - branch (str): The name of the branch. Default is 'main'.

        Returns:
        str: The SHA of the latest commit on the specified branch.
        """
        endpoint = f"git/ref/heads/{branch}"
        return self._make_request("GET", endpoint)["data"]["object"]["sha"]

    def create_branch(self, branch_name: str, commit_sha: str):
        """
        Create a new branch based on a specific commit.

        Parameters:
        - branch_name (str): The name of the new branch.
        - commit_sha (str): The SHA of the commit to base the new branch on.

        Returns:
        bool: True if the branch creation is successful, False otherwise.
        """
        endpoint = "git/refs"
        data = {"ref": f"refs/heads/{branch_name}", "sha": commit_sha}
        response = self._make_request("POST", endpoint, data)
        return response["status_code"] == 201

    def create_blob(self, content: str):
        """
        Create a new Git blob.

        Parameters:
        - content (str): The content of the blob.

        Returns:
        str: The SHA of the created blob.
        """
        endpoint = "git/blobs"
        payload = {"content": content, "encoding": "utf-8"}
        return self._make_request("POST", endpoint, payload)["data"]["sha"]

    def create_tree(self, base_tree_sha: str, blobs: list):
        """
        Create a new Git tree.

        Parameters:
        - base_tree_sha (str): The SHA of the base tree.
        - blobs (list): List of dictionaries, each containing 'path' and 'blob_sha' keys.

        Returns:
        str: The SHA of the created tree.
        """
        endpoint = "git/trees"
        tree = [
            {
                "path": blob["path"],
                "mode": "100644",
                "type": "blob",
                "sha": blob["blob_sha"],
            }
            for blob in blobs
        ]
        payload = {"base_tree": base_tree_sha, "tree": tree}
        return self._make_request("POST", endpoint, payload)["data"]["sha"]

    def create_commit(
        self, message: str, branch_name: str, tree_sha: str, parent_sha: str
    ):
        """
        Create a new Git commit and update the branch reference.

        Parameters:
        - message (str): The commit message.
        - branch_name (str): The name of the branch to update.
        - tree_sha (str): The SHA of the tree associated with the commit.
        - parent_sha (str): The SHA of the parent commit.

        Returns:
        str: The SHA of the newly created commit.
        """
        endpoint_commit = "git/commits"
        data_commit = {
            "message": message,
            "tree": tree_sha,
            "parents": [parent_sha],
        }
        new_commit_sha = self._make_request(
            "POST", endpoint_commit, data_commit
        )["data"]["sha"]

        endpoint_update_ref = f"git/refs/heads/{branch_name}"
        payload = {"sha": new_commit_sha}
        self._make_request("PATCH", endpoint_update_ref, payload)

        return new_commit_sha

    def create_pull_request(
        self, title: str, body: str, head: str, base: str = "main"
    ):
        """
        Create a new pull request.

        Parameters:
        - title (str): The title of the pull request.
        - body (str): The description or body of the pull request.
        - head (str): The name of the branch where changes are pushed.
        - base (str): The name of the branch where changes are pulled. Default is 'main'.

        Returns:
        dict: Information about the created pull request.
        """
        endpoint = "pulls"
        payload = {"title": title, "body": body, "head": head, "base": base}
        return self._make_request("POST", endpoint, payload)["data"]
