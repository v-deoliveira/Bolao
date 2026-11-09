from .db import get_db
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
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

# A separate function to update points for a specific match, so it can be called from the sync_results function, after updating the match scores.
def sync_bets(match_id, home_score, away_score):
    db = get_db()
    bets = db.execute(
        """
            SELECT id, home_score, away_score
            FROM predictions
            WHERE match_id = ?
        """,
        (match_id,)
    )
    for bet in bets:
        pts = calculate_points(home_score, away_score, bet['home_score'], bet['away_score'])
        db.execute(
            "UPDATE predictions SET points = ? WHERE id = ?",
            (pts, bet['id'])
        )


def format_season_label(season):
    if season['start_date'][:4] != season['end_date'][:4]:
        return f"{season['start_date'][:4]}/{season['end_date'][2:4]}"
    else:
        return f"{season['start_date'][:4]}"


# This function will format the stored naive UTC date, into an aware object. Then will convert it to the users timezone.
# Will return the data in a better format for user reading, wiht the option to adjust this format as needed.
def format_datetime_tz(value, tz_name=None, fmt="%d %b %Y, %H:%M"):
    dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    if tz_name:
        try:
            dt = dt.astimezone(ZoneInfo(tz_name))
        except Exception:
            pass

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