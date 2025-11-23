from pydantic import BaseModel

class Querries(BaseModel):
    team_name: str
    user_id: str