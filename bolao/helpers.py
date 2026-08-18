from .db import get_db

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

def delete_helper(id, table_name):
    db = get_db()
    try:
        db.execute(
            f"DELETE FROM {table_name} WHERE id = ?", (id,)
        )
        db.commit()
        return True
    except db.IntegrityError:
        return False