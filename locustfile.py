from locust import FastHttpUser, task, between, constant_pacing
from tests.load_test.scenarios.team import TeamScenario
from tests.load_test.scenarios.users import UserScenario
from tests.load_test.scenarios.pull_requests import PullRequestScenarios

class TesterUser(FastHttpUser):
        wait_time = constant_pacing(1)
        tasks = {
            TeamScenario: 1,
            UserScenario: 5,
            PullRequestScenarios: 10
        }
