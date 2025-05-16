# .github/actions/check-sensitive-files/check.py
import os
import sys
import requests


def post_comment(pr_number, message, token):
    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    payload = {"body": message}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code >= 400:
        print(f"Failed to post comment: {response.status_code}, {response.text}")

def close_pull_request(pr_number, token):
    url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/pulls/{pr_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    payload = {"state": "closed"}
    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code >= 400:
        print(f"Failed to close PR: {response.status_code}, {response.text}")

token = sys.argv[1]
if not token:
    raise RuntimeError("GITHUB_TOKEN environment variable is not set")
repo = os.environ['GITHUB_REPOSITORY']
pr_number = sys.argv[2]

locked_file_path = ".lockedFiles"


if not os.path.exists(locked_file_path):
    post_comment(pr_number, "lockedFile.txt is missing.", token)
    sys.exit(2)

with open(locked_file_path, "r") as f:
    sensitive_files = [line.strip() for line in f if line.strip()]


headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github.v3+json"
}

label_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/labels"
labels_resp = requests.get(label_url, headers=headers)
print("Label API response:", labels_resp.status_code, labels_resp.text)
labels = [label['name'] for label in labels_resp.json()]
print("Labels found on PR:", labels)
for label in labels:
    if label=="BYPASS_LABEL":
        post_comment(pr_number, "BYPASS_LABEL was used", token)
        sys.exit(0)

files_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
files_resp = requests.get(files_url, headers=headers)
changed_files = [file['filename'] for file in files_resp.json()]

sensitive_changes = [f for f in changed_files if f in sensitive_files]


if sensitive_changes:
    msg = "\n".join([f"❌ Sensitive file changed: `{f}`" for f in sensitive_changes])
    post_comment(pr_number, msg, token)
    close_pull_request(pr_number, token)
    exit(1)
else:
    post_comment(pr_number, "✅ No sensitive files changed.", token)

