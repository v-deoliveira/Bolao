DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS seasons;
DROP TABLE IF EXISTS tournaments;
DROP TABLE IF EXISTS areas;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE areas (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL,
    flag TEXT,
    parent_area_id INTEGER REFERENCES areas(id)
);

CREATE TABLE tournaments (
    id INTEGER PRIMARY KEY,
    area_id INTEGER NOT NULL REFERENCES areas(id),
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    type TEXT NOT NULL,
    emblem TEXT
);

CREATE TABLE seasons (
    id INTEGER PRIMARY KEY,
    tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
    start_date TEXT,
    end_date TEXT
);

CREATE TABLE teams (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    short_name TEXT,
    tla TEXT NOT NULL,
    crest TEXT
);

CREATE TABLE matches (
    id INTEGER PRIMARY KEY,
    season_id INTEGER NOT NULL REFERENCES seasons(id),
    utc_date TEXT,
    status TEXT NOT NULL,
    matchday INTEGER,
    stage TEXT NOT NULL,
    group_name TEXT,
    home_team INTEGER NOT NULL REFERENCES teams(id),
    away_team INTEGER NOT NULL REFERENCES teams(id),
    home_score INTEGER,
    away_score INTEGER,
    pso_home_score INTEGER,
    pso_away_score INTEGER
);

CREATE TABLE predictions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    home_score INTEGER NOT NULL,
    away_score INTEGER NOT NULL,
    points INTEGER DEFAULT 0,

    UNIQUE(user_id, match_id),

    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (match_id) REFERENCES matches (id) ON DELETE CASCADE
);
