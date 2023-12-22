# github-repo-toolz

The class `GithubRepo` gives you the functionality for all the steps to programatically create a Pull Request to an existing Github repo from your own files. You will need to provide a Github `access token` that has access to making pull requests in the specified repository in order for it to work.

## How it works

Instead of using a library like `Git Python`, `github-repo-toolz` uses the Github API directly in order to create the Pull Request. The usage example as well as the docstrings in `github_repo.py` should give more detail on the functionality.

## Usage Example

```
from github_repo import GitHubRepo

owner = <GITHUB_REPO_OWNER>
repo = <GITHUB_REPO_NAME>
token = <GITHUB_ACCESS_TOKEN>
origin_branch = "main"

github = GitHubRepo(
    owner,
    repo,
    token,
)

# get the gitsha of the commit you want to branch off of, defaults to "main"
latest_commit_sha = github.get_latest_commit_sha(origin_branch)

# this is the name of the branch for your pull request
branch_name = <NEW_BRANCH_NAME>
github.create_branch(branch_name, latest_commit_sha)

# the example files are in this repo, this is to give a robust explanation of adding/creating blobs for multiple files

sample_files = ["sample_files/sample_app.py", "sample_files/sample_doc.md"]
blobs = []
for file_path in sample_files:
    with open(file_path, "r") as file:
        file_content = file.read()

    # you'll create a blob per file
    blob_sha = github.create_blob(file_content)

    # you can specify whatever file_path you want for Github
    blobs.append({"blob_sha": blob_sha, "path": file_path})

# create a tree from the latest commit sha and add all the files you want to it
tree_sha = github.create_tree(latest_commit_sha, blobs)

commit_message = <COMMIT_MESSAGE>
new_commit_sha = github.create_commit(
    commit_message,
    branch_name,
    tree_sha,
    latest_commit_sha,
)

title = <PR_TITLE>
description = <PR_DESCRIPTION>
create_pr = github.create_pull_request(
    title,
    description,
    branch_name,
    origin_branch,
)
```

If all goes well, you should see a pull request from your `branch_name` to `origin_branch`.