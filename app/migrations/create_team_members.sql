CREATE TABLE team_members (
    team_name TEXT REFERENCES teams(team_name) ON DELETE CASCADE,
    user_id TEXT REFERENCES users(user_id) ON DELETE CASCADE,
    PRIMARY KEY(team_name, user_id)
);