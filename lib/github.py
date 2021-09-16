import re
from github import Github, PullRequest

GITHUB_ACCESS_TOKEN="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"
CLOUD_REPO_NAME = 'PropertyBrands/btt-ngt-d7'

def get_cloud_pr(pr_number: int) -> PullRequest:
    return Github(GITHUB_ACCESS_TOKEN).get_repo(CLOUD_REPO_NAME).get_pull(pr_number)

def extract_monikers_from_cloud_pr(pr: PullRequest) -> list:
    if pr.body and '<moniker>' in pr.body:
        return re.sub(r'(<monikers>|</monikers>)', '', pr.body).split(',')
    else:
        return ['nbtm']
    
    

