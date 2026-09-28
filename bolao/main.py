from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from .auth import login_required
from .db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()

    predictions = db.execute(
        """
            SELECT home.name AS home_team,
                away.name AS away_team,
                matches.id AS match_id,
                predictions.home_score AS home_score,
                predictions.away_score AS away_score,
                matches.utc_date,
                matches.status,
                predictions.points,
                matches.home_score AS ft_home_score,
                matches.away_score AS ft_away_score
            FROM predictions
            JOIN teams AS home
                ON home.id = matches.home_team
            JOIN teams AS away
                ON away.id = matches.away_team
            JOIN matches
                ON matches.id = predictions.match_id
            WHERE predictions.user_id = ?
        """,
        (g.user["id"],)   
    ).fetchall()

    return render_template("main/index.html", predictions=predictions)

@bp.route('/matches', methods=('GET',))
@login_required
def matches():
    db = get_db()

    tournaments = db.execute(
        """
            SELECT * FROM tournaments
        """
    ).fetchall()

    # If no tournaments available(when database is empty) redirect to main.index with flash message
    if not tournaments:
        flash("No matches available yet.")
        return redirect(url_for("main.index"))

    # When no tournament selected, tournament_id will be first tournament from tournaments
    tournament_id = request.args.get("tournament")
    if tournament_id is None:
        tournament_id = tournaments[0]["id"]

    seasons = db.execute(
        "SELECT * FROM seasons WHERE tournament_id = ? ORDER BY start_date DESC",
        (tournament_id,)
    ).fetchall()
    
    selected_season_id = request.args.get("season")
    if selected_season_id is None:
        selected_season_id = seasons[0]['id']

    matches = db.execute(
        """
            SELECT home.name AS home_team, 
                away.name AS away_team, 
                matches.id, 
                matches.home_score, 
                matches.away_score, 
                matches.utc_date, 
                matches.status,
                matches.matchday
            FROM matches
            JOIN teams AS home
                ON home.id = matches.home_team
            JOIN teams AS away
                ON away.id = matches.away_team
            WHERE matches.season_id = ?
            ORDER BY matches.utc_date, matches.matchday
        """,
        (selected_season_id,)
    ).fetchall()

    tournament = db.execute(
        """
            SELECT name, code, type, emblem
            FROM tournaments
            WHERE id = ?
        """,
        (tournament_id,)
    ).fetchone()

    return render_template("main/matches.html", tournaments=tournaments,
                            matches=matches, 
                            tournament=tournament,
                            seasons=seasons)


@bp.route('/ranking', methods=('GET', 'POST'))
@login_required
def ranking():
    db = get_db()
    # Let's keep a limit of 10 users in the ranking, for now.
    users = db.execute(
        """
            SELECT users.username,
                COALESCE(SUM (predictions.points), 0) AS points
            FROM users
            LEFT JOIN predictions
                ON predictions.user_id = users.id
            GROUP BY users.username
            ORDER BY points DESC
            LIMIT 10
        """
    ).fetchall()
    return render_template("main/ranking.html", users=users)