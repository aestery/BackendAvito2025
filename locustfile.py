from locust import FastHttpUser, task, between
from tests.load_test.scenarios.team import TeamScenario

class TesterUser(FastHttpUser):
        tasks = {
            TeamScenario: 10
        }
