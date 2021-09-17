import re
from github import Github, PullRequest


class GithubHelper():

    def __init__(self, token: str, repo_name: str):
        self.token = token
        self.client = Github(self.token)
        self.repo_name = repo_name

    def get_token(self):
        return self.token

    def get_pr(self, pr_number: int) -> PullRequest:
        return self.client.get_repo(self.repo_name).get_pull(pr_number)

    def extract_monikers_from_cloud_pr(self, pr: PullRequest) -> list:
        if pr.body and '<monikers>' in pr.body:
            return re.sub(r'(<monikers>|</monikers>)', '', pr.body).split(',')
        else:
            return ['nbtm']
