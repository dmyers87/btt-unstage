import re
from github import Github, PullRequest

class GithubHelper():

    def __init__(self, token, cloud_repo_name):
        self.token = token
        self.client = Github(self.token)
        self.cloud_repo_name = cloud_repo_name

    def get_token(self):
        return self.token

    def get_cloud_pr(self, pr_number: int) -> PullRequest:
        return self.client.get_repo(self.cloud_repo_name).get_pull(pr_number)

    def extract_monikers_from_cloud_pr(pr: PullRequest) -> list:
        if pr.body and '<monikers>' in pr.body:
            return re.sub(r'(<monikers>|</monikers>)', '', pr.body).split(',')
        else:
            return ['nbtm']

