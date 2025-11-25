from locust import TaskSet, task
from locust.contrib.fasthttp import ResponseContextManager
from app.models.error_response import ErrorCode
from tests.load_test.scenarios.utils import (
    ScenarioParameters, 
    is_expected_error
)

class PullRequestScenarios(TaskSet):
    _base_route = "/pullRequest"
    _utils = ScenarioParameters()

    @task(2)
    def create_pull_request(self): 
        pull_request_id = self._utils.get_pr_id()
        user_id = self._utils.get_user_id()
        self._create_handler(pull_request_id, pull_request_id, user_id)

    @task(2)
    def merge_pull_request(self):
        pull_request_id = self._utils.get_prob_exist_pr()
        self._merge_handler(pull_request_id)

    @task(4)
    def reassign_reviewer(self): 
        pull_request_id = self._utils.get_prob_exist_pr()
        reviewer_id = self._utils.get_user_id()
        self._reassign_handler(pull_request_id, reviewer_id)

    def _create_handler(self,
            pull_request_id: str,
            pull_request_name: str, 
            author_id: str
            ):
        
        with self._create(
            pull_request_id,
            pull_request_name, 
            author_id
            ) as response:
            try:
                if response.status_code == 201:
                    response.success()
                elif is_expected_error(response, 404, ErrorCode.NOT_FOUND):
                    response.success()
                elif is_expected_error(response, 409, ErrorCode.PR_EXISTS):
                    response.success()
            except:
                response.failure("failed to create pr")

    def _merge_handler(self, pull_request_id: str):
        with self._merge(pull_request_id) as response:
            try:
                if response.status_code == 200:
                    response.success()
                elif is_expected_error(response, 404, ErrorCode.NOT_FOUND):
                    response.success()
            except:
                response.failure("failed to merge")

    def _reassign_handler(self, pull_request_id: str, old_user_id: str):
        with self._reassign(pull_request_id, old_user_id) as response:
            try:
                if response.status_code == 200:
                    print("probability check")
                    response.success()
                elif is_expected_error(response, 404, ErrorCode.NOT_FOUND):
                    response.success()
                elif is_expected_error(response, 409, ErrorCode.PR_MERGED):
                    response.success()
                elif is_expected_error(response, 409, ErrorCode.NOT_ASSIGNED):
                    response.success()
                elif is_expected_error(response, 409, ErrorCode.NO_CANDIDATE):
                    response.success
            except:
                response.failure("failed to reassign")
    
    def _create(self, 
            pull_request_id: str,
            pull_request_name: str, 
            author_id: str
            ) -> ResponseContextManager:
        return self.client.post(
            f"{self._base_route}/create",
            catch_response=True,
            json={
                "pull_request_id": pull_request_id,
                "pull_request_name": pull_request_name, 
                "author_id": author_id
            }
        )
    
    def _merge(self, pull_request_id: str) -> ResponseContextManager:
        return self.client.post(
            f"{self._base_route}/merge",
            catch_response=True,
            json={"pull_request_id": pull_request_id}
        )
    def _reassign(self, 
            pull_request_id: str, 
            old_user_id: str
            ) -> ResponseContextManager:
        return self.client.post(
            f"{self._base_route}/reassign",
            catch_response=True,
            json={
                "pull_request_id": pull_request_id,
                "old_user_id": old_user_id
                }
        )
