from enum import Enum

class Tags(str, Enum):
    TEAMS = "Teams"
    USERS = "Users"
    PULL_REQUESTS = "PullRequests"
    HEALTH = "Health"