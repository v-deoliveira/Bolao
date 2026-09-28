from .db import get_db
from datetime import datetime

def outcome(home_score, away_score):
    if home_score > away_score:
        return "H"
    if home_score < away_score:
        return "A"
    return "D"


def calculate_points(match_home, match_away, bet_home, bet_away):
    if (bet_home, bet_away) == (match_home, match_away):
        return 3
    if outcome(bet_home, bet_away) == outcome(match_home, match_away):
        return 1
    return 0


def format_season(season):
    if season['start_date'][:4] != season['end_date'][:4]:
        return f"{season['start_date'][:4]}/{season['end_date'][2:4]}"
    else:
        return f"{season['start_date'][:4]}"


# Format the api's date format to a better user readable format. It will be called from the template itself,
# with the option to add a custom format, if needed.
def format_datetime(value, fmt="%d %b %Y, %H:%M"):
    dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    return dt.strftime(fmt)

# Using the approach of prebuilt queries, so the value of table_name will be filtered by _DELETE_QUERIES
_DELETE_QUERIES = {
    "matches": "DELETE FROM matches WHERE id = ?",
    "teams": "DELETE FROM teams WHERE id = ?",
    "tournaments": "DELETE FROM tournaments WHERE id = ?",
}
def delete_helper(id, table_name):
    query = _DELETE_QUERIES.get(table_name)
    if query is None:
        raise ValueError(f"Unknown table: {table_name}")
    db = get_db()
    try:
        db.execute(query, (id,))
        db.commit()
        return True
    except db.IntegrityError:
        return False