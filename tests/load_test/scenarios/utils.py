import random
from app.models.error_response import ErrorCode


def is_expected_error(response, status_code: int, error_code: ErrorCode):
    return (
        response.status_code == status_code
        and response.json()["error"]["code"] == error_code.value
    )

class ScenarioParameters:
    def __init__(self) -> None:
        self._max_team_number = 20
        self._min_team_number = 0

        self._min_team_size = 5
        self._max_team_size = 10

        self._min_pr_id = 0
        self._max_pr_id = 1000

        self._existing_pr = []

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
    
    def get_pr_id(self) -> str:
        pr_id = random.randint(
            self._min_pr_id,
            self._max_pr_id
        )
        return str(pr_id)
    
    def create_pr(self, pr_id: str) -> None:
        self._existing_pr.append(pr_id)
    
    def get_prob_exist_pr(self) -> str:
        """returns pr that probably exists"""
        is_exist = random.randint(0,4)
        if is_exist and len(self._existing_pr) != 0:
            index = random.randint(0, (len(self._existing_pr)-1))
            return self._existing_pr[index]
        return self.get_pr_id()
    