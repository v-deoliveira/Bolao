from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from .auth import login_required
from .db import get_db

bp = Blueprint('predictions', __name__, url_prefix='/predictions')

@bp.route('/match/<int:match_id>/make_bet', methods=('GET', 'POST'))
@login_required
def make_bet(match_id):
    db = get_db()
    if request.method == "POST":
        try:
            home_score = int(request.form.get("home_score"))
            away_score = int(request.form.get("away_score"))
        except ValueError:
            flash("Invalid input. Must be a positive number.")
            return redirect(url_for("predictions.make_bet", match_id=match_id))

        # Checks for a positive int
        if home_score < 0 or away_score < 0:
           flash("Score must be positive")
           return redirect(url_for("predictions.make_bet", match_id=match_id))
        
        error = None
        try:
            db.execute(
                "INSERT INTO predictions (user_id, match_id, home_score, away_score) VALUES (?, ?, ?, ?)",
                (g.user["id"], match_id, home_score, away_score),
            )
            db.commit()
        except db.IntegrityError:
            error = "INVALID MATCH OR BET ALREADY EXIST - CHECK YOUR BETS"

        flash(error) if error is not None else flash("Bet placed successfully")
        return redirect(url_for("predictions.make_bet", match_id=match_id))

    match = db.execute(
        """
            SELECT home.name AS home_team, 
                away.name AS away_team,
                home.tla AS home_tla,
                away.tla AS away_tla,
                home.crest AS home_crest,
                away.crest AS away_crest
            FROM matches
            JOIN teams AS home
                ON home.id = matches.home_team
            JOIN teams AS away
                ON away.id = matches.away_team
            WHERE matches.id = ?
        """,
        (match_id,)
    ).fetchone()

    return render_template("predictions/make_bet.html", match=match)