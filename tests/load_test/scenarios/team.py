import random
from locust import TaskSet, task
from locust.contrib.fasthttp import ResponseContextManager
from app.models.team import Team, TeamMember
from app.models.error_response import ErrorCode
from tests.load_test.scenarios.utils import ScenarioParameters, is_expected_error


class TeamScenario(TaskSet):
    _base_route = "/team"
    _utils = ScenarioParameters()

    @task(1)
    def create_team(self):
        team_number = self._utils.get_team_number()
        team = Team(
            team_name=f"name_{team_number}",
            members=[
                TeamMember(
                    user_id = f'id_{i}{team_number}',
                    username = f"username_{i}",
                    is_active = True
                ) 
                for i in range(self._utils.get_team_size())
            ]
        )
        self._handle_add_response(team=team)
    
    @task(10)
    def get_team(self):
        team_number = self._utils.get_team_number()
        team_name=f"name_{team_number}"
        self._handle_get_response(team_name=team_name)

    def _handle_get_response(self, team_name: str):
        with self._get(team_name=team_name) as response:
            if response.status_code == 200:
                response.success()
            elif is_expected_error(response, 404, ErrorCode.NOT_FOUND):
                response.success()
            
    def _get(self, team_name: str) -> ResponseContextManager:
        return self.client.get(
            f"{self._base_route}/get",
            catch_response=True,
            params={"team_name": team_name}
            )

    def _handle_add_response(self, team: Team):
        with self._add(team=team) as response:
            if response.status_code == 201:
                response.success()
            elif is_expected_error(response, 400, ErrorCode.TEAM_EXISTS):
                response.success()

    def _add(self, team: Team) -> ResponseContextManager:
        return self.client.post(
            f"{self._base_route}/add",
            catch_response=True,
            json={
                "team_name": team.team_name,
                "members": [{
                        "user_id": member.user_id,
                        "username": member.username,
                        "is_active": member.is_active
                    } 
                    for member in team.members
                ]
            }
        )
