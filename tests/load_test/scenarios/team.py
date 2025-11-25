from locust import TaskSet, User, task
from locust.contrib.fasthttp import FastHttpSession, ResponseContextManager
from app.models.team import Team, TeamMember
from app.models.error_response import ErrorCode


class TeamScenario(TaskSet):
    _base_route = "/team"

    @task
    def create_team(self):
        team = Team(
            team_name="name",
            members=[
                TeamMember(
                    user_id = 'id',
                    username = "username",
                    is_active = True
                )
            ]
        )
        self._handle_add_response(team=team)
    
    def _handle_get_response(self, team_name: str):
        with self._get(team_name=team_name) as response: ...

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
            if (
                response.status_code == 400 and 
                response.json()["error"]["code"] == ErrorCode.TEAM_EXISTS.value
                ):
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
