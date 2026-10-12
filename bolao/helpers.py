from .db import get_db
from datetime import datetime
from flask import g

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


# Function to insert points into he predictions table. It will be called from the homepage, if there are any matches that have finshed status and the user has made a bet for it.
def insert_points():
    db = get_db()
    data = db.execute(
        """
            SELECT predictions.id AS bet_id,
            predictions.home_score AS bet_home_score,
            predictions.away_score AS bet_away_score,
            matches.home_score,
            matches.away_score,
            matches.status
            FROM predictions
            JOIN matches
                ON matches.id == predictions.match_id
            WHERE matches.status = 'FINISHED'   
        """,
    ).fetchall()

    # Made a mistake earlier, updating without using the bet_id, so it was updating all the rows with the same points, instead of updating each row with its own points.
    for b in data:
        pts = calculate_points(b['home_score'], b['away_score'], b['bet_home_score'], b['bet_away_score'])
        db.execute(
            "UPDATE predictions SET points = ? WHERE id = ?",
            (pts, b['bet_id'])
        )


def format_season_label(season):
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