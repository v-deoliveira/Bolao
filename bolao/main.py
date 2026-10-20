from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from .auth import login_required
from .db import get_db
from zoneinfo import ZoneInfo
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()

    predictions = db.execute(
        """
            SELECT tournaments.name AS tournament_name,
                tournaments.emblem AS tournament_emblem,
                tournaments.code AS tournament_code,
                home.short_name AS home_short_name,
                home.tla AS home_tla,
                home.crest AS home_crest,
                away.short_name AS away_short_name,
                away.tla AS away_tla,
                away.crest AS away_crest,
                predictions.home_score AS home_score,
                predictions.away_score AS away_score,
                matches.utc_date,
                matches.status,
                predictions.points,
                matches.home_score AS ft_home_score,
                matches.away_score AS ft_away_score
            FROM predictions
            JOIN seasons
                ON seasons.id = matches.season_id
            JOIN tournaments
                ON tournaments.id = seasons.tournament_id
            JOIN teams AS home
                ON home.id = matches.home_team
            JOIN teams AS away
                ON away.id = matches.away_team
            JOIN matches
                ON matches.id = predictions.match_id
            WHERE predictions.user_id = ?
            ORDER BY matches.utc_date
        """,
        (g.user["id"],)   
    ).fetchall()

    return render_template("main/index.html", predictions=predictions)

@bp.route('/tournament/<int:id>', methods=('GET', ))
@login_required
def tournament(id):
    db = get_db()

    tournament = db.execute(
        "SELECT id, name, code, emblem FROM tournaments WHERE id = ?", (id,)
    ).fetchone()
    
    seasons = db.execute(
        "SELECT * FROM seasons WHERE tournament_id = ? ORDER BY start_date DESC",
        (id,)
    ).fetchall()

    selected_season_id = request.args.get("season")
    if selected_season_id is None:
        selected_season_id = seasons[0]['id']

    matches = db.execute(
            """
                SELECT home.short_name AS home_short_name, 
                    away.short_name AS away_short_name,
                    home.crest AS home_crest,
                    away.crest AS away_crest,
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

    return render_template('main/matches.html', tournament=tournament,
                            seasons=seasons,
                            matches=matches)

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

# This function will be executed before every request, and it will load the tournaments from the database and store them in the g object, which is a global object that can be accessed from any view function. 
# This way, we can display them in the navigation bar.
@bp.before_app_request
def load_tournamenst():
    g.tournaments = get_db().execute(
        """
            SELECT tournaments.id,
                tournaments.name,
                tournaments.code,
                tournaments.emblem,
                areas.flag
                FROM tournaments
                JOIN areas
                    ON areas.id = tournaments.area_id
                WHERE tournaments.type = 'LEAGUE'
                ORDER BY areas.id DESC, tournaments.name
        """
    ).fetchall()


@bp.route('/set-timezone', methods=('POST',))
@login_required
def set_timezone():
    return "", 204
