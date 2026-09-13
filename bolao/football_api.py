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

def test(id):
    data = _get(f"/competitions/{id}/teams")
    return data