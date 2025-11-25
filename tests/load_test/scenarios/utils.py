import random
from app.models.error_response import ErrorCode


def is_expected_error(response, status_code: int, error_code: ErrorCode):
    return (
        response.status_code == status_code
        and response.json()["error"]["code"] == error_code.value
    )

class ScenarioParameters:
    def __init__(self) -> None:
        self._max_team_number = 200
        self._min_team_number = 0

        self._min_team_size = 5
        self._max_team_size = 20

    def get_team_size(self) -> int: 
        return random.randint(
            self._min_team_size,
            self._max_team_size
            )
    
    def get_team_number(self) -> int:
        return random.randint(
            self._min_team_number,
            self._max_team_number
        )
    
    def get_user_id(self) -> str:
        member_id = random.randint(0,self._max_team_size)
        team_id = self.get_team_number()
        return f"id_{member_id}{team_id}"
    
    def get_status(self) -> bool:
        return bool(random.randint(0,3))
    