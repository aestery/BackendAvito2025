from locust import ( 
    TaskSet, 
    task
)
from locust.contrib.fasthttp import ResponseContextManager
from app.models.error_response import ErrorCode
from tests.load_test.scenarios.utils import (
    ScenarioParameters, 
    is_expected_error
)

class UserScenario(TaskSet):
    _base_route = "/users"
    _utils = ScenarioParameters()

    @task(1)
    def get_review(self): 
        user_id = self._utils.get_user_id()
        self._get_review_handler(user_id=user_id)

    @task(3)
    def set_activity(self):
        user_id = self._utils.get_user_id()
        is_active = self._utils.get_status()
        self._set_is_active_handler(user_id=user_id, is_active=is_active)

    def _get_review_handler(self, user_id: str):
        with self._get_review(user_id) as response:
            if response.status_code == 200:
                    response.success()

    def _set_is_active_handler(self, user_id: str, is_active: bool):
        with self._set_is_active(user_id, is_active) as response:
            if response.status_code == 200:
                response.success()
            elif is_expected_error(response, 404, ErrorCode.NOT_FOUND): 
                response.success()

    def _get_review(self, user_id: str) -> ResponseContextManager: 
        return self.client.get(
            f"{self._base_route}/getReview",
            catch_response=True,
            params={"user_id": user_id}
        )
    
    def _set_is_active(self, user_id: str, is_active: bool) -> ResponseContextManager:
         return self.client.post(
            f"{self._base_route}/setIsActive",
            catch_response=True,
            json={
                 "user_id": user_id,
                 "is_active": is_active
            }
         )
