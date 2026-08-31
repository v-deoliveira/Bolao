import requests
from flask import current_app

BASE_URL = 'https://api.football-data.org/v4'

def _get(path, params=None):
    headers = {"X-Auth-Token": current_app.config["API_TOKEN"]}
    response = requests.get(f"{BASE_URL}{path}", headers=headers, params=params, timeout=0.5) #Need to better understand 'timeout'
    response.raise_for_status()
    return response.json()

def  get_competitions():
    return _get("/competitions")

def get_matches(competition_id, **params):
    return _get(f"/competitions/{competition_id}/matches", params=params) #params here can be season, dateFrom, dateTo, matchday, status, stage, group, etc.
