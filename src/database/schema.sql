-- src/database/schema.sql

-- Takımlar tablosu
CREATE TABLE IF NOT EXISTS teams (
    team_id INTEGER PRIMARY KEY,
    team_name VARCHAR(100) NOT NULL,
    team_short_name VARCHAR(50),
    team_tla VARCHAR(10),
    crest_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sezonlar tablosu
CREATE TABLE IF NOT EXISTS seasons (
    season_id INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_code VARCHAR(10),
    competition_name VARCHAR(100),
    season_start DATE,
    season_end DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Puan durumu tablosu
CREATE TABLE IF NOT EXISTS standings (
    standing_id INTEGER PRIMARY KEY AUTOINCREMENT,
    season_id INTEGER,
    team_id INTEGER,
    position INTEGER,
    played_games INTEGER,
    won INTEGER,
    draw INTEGER,
    lost INTEGER,
    points INTEGER,
    goals_for INTEGER,
    goals_against INTEGER,
    goal_difference INTEGER,
    form VARCHAR(10),
    form_points INTEGER,
    win_percentage DECIMAL(5,2),
    points_per_game DECIMAL(4,2),
    goals_per_game DECIMAL(4,2),
    goals_conceded_per_game DECIMAL(4,2),
    last_updated TIMESTAMP,
    FOREIGN KEY (season_id) REFERENCES seasons(season_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- Maçlar tablosu
CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    season_id INTEGER,
    match_date DATE,
    match_time TIME,
    matchday INTEGER,
    home_team_id INTEGER,
    away_team_id INTEGER,
    home_score INTEGER,
    away_score INTEGER,
    home_score_ht INTEGER,
    away_score_ht INTEGER,
    status VARCHAR(20),
    total_goals INTEGER,
    goal_difference INTEGER,
    is_draw INTEGER,
    is_home_win INTEGER,
    is_away_win INTEGER,
    referees TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (season_id) REFERENCES seasons(season_id),
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
);

-- İndeksler for performans
CREATE INDEX idx_matches_date ON matches(match_date);
CREATE INDEX idx_matches_teams ON matches(home_team_id, away_team_id);
CREATE INDEX idx_standings_position ON standings(position);
CREATE INDEX idx_standings_team ON standings(team_id);