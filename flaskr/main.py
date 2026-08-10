from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from . auth import login_required
from . db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()

    predictions = db.execute(
        """
            SELECT competitions.name AS tournament,
                competitions.season AS season,
                home.name AS home_team,
                away.name AS away_team,
                matches.id AS match_id,
                predictions.home_score AS home_score,
                predictions.away_score AS away_score,
                matches.match_date AS match_date,
                matches.status AS match_status,
                predictions.points
            FROM predictions
            JOIN competitions
                ON competitions.id = matches.competition_id
            JOIN teams AS home
                ON home.id = matches.home_team_id
            JOIN teams AS away
                ON away.id = matches.away_team_id
            JOIN matches
                ON matches.id = predictions.match_id
            WHERE predictions.user_id = ?
        """,
        (g.user["id"],)   
    ).fetchall()

    return render_template("main/index.html", predictions=predictions)

@bp.route('/matches', methods=('GET', 'POST'))
@login_required
def matches():
    db = get_db()

    competitions = db.execute(
        """
            SELECT * FROM competitions
            ORDER BY season
        """
    ).fetchall()

    matches = db.execute(
        """
            SELECT home.name AS home_team, 
                away.name AS away_team, 
                matches.id, 
                matches.home_score, 
                matches.away_score, 
                matches.match_date, 
                matches.status
            FROM matches
            JOIN teams AS home
                ON home.id = matches.home_team_id
            JOIN teams AS away
                ON away.id = matches.away_team_id
            WHERE matches.competition_id = ?
            ORDER BY matches.match_date
        """,
        (request.args.get("competition"),)
    ).fetchall()

    tournament = db.execute(
        """
            SELECT * FROM competitions
            WHERE id = ?
        """,
        (request.args.get("competition"),)
    ).fetchone()

    return render_template("main/matches.html", competitions=competitions,
                            matches=matches, 
                            tournament=tournament)
