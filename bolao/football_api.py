import requests
from flask import current_app
from .db import get_db

BASE_URL = 'https://api.football-data.org/v4'

def _get(path, params=None):
    headers = {"X-Auth-Token": current_app.config["API_TOKEN"]}
    response = requests.get(f"{BASE_URL}{path}", headers=headers, params=params) #Need to better understand 'timeout'
    print(response.url)
    response.raise_for_status()
    return response.json()

def  get_competitions():
    data = _get("/competitions")
    return data["competitions"]

def get_matches(competition_id, **params):
    data = _get(f"/competitions/{competition_id}/matches", params=params) #params here can be season, dateFrom, dateTo, matchday, status, stage, group, etc.
    return data["matches"]

def get_areas(competitions):
    areas = [c["area"] for c in competitions]
    return areas

def get_teams(competition_id):
    db = get_db()
    data = _get(f"/competitions/{competition_id}/teams")
    for team in data['teams']:
        if team.get('id') is None:
            raise KeyError(f"MISSING ID FOR '{team.get('name')}'.")
        db.execute(
            """
                INSERT INTO teams (crest, id, name, short_name, tla) VALUES(?, ?, ?, ?, ?)
                ON CONFLICT (id) DO NOTHING
            """,
            (team.get('crest'), team.get('id'), team.get('name'), team.get('shortName'), team.get('tla')),
        )


def create_matches(matches):
    db = get_db()
    for match in matches:
        if match.get('id') is None:
            raise KeyError("API RESPONSE MISSING MATCH ID")
        
        away_id = match.get('awayTeam', {}).get('id')
        home_id = match.get('homeTeam', {}).get('id')
        season_id = match.get('season', {}).get('id')

        if away_id is None or home_id is None:
            raise KeyError(f"MATCH (id: {match.get('id')}) MISSING A TEAM'S ID.")
        if season_id is None:
            raise KeyError(f"MATCH (id: {match.get('id')}) MISSING SEASON'S ID.")

        score = match.get('score', {}).get('fullTime')

        db.execute(
            """
                INSERT INTO matches (away_team, home_team, group_name, id, matchday, away_score, home_score, season_id, stage, status, utc_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO NOTHING
            """,
            (away_id, home_id, match.get('group'), match.get('id'), match.get('matchday'), score.get('away'), score.get('home'), season_id, match.get('stage'), match.get('status'), match.get('utcDate')),
        )

