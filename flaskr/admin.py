from functools import wraps

from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        
        #Check if is admin
        if not g.user["is_admin"]:
            abort(403)

        return view(**kwargs)
    
    return wrapped_view

@bp.route('/', methods=('GET', 'POST'))
@admin_required
def index():
    db = get_db()
    matches = None
    competitions = db.execute(
        """
            SELECT * FROM competitions
            ORDER BY name, season
        """
    ).fetchall()
    
    teams = db.execute(
        """
            SELECT * FROM teams
            ORDER BY name
        """
    ).fetchall()

    return render_template("admin/admin.html", 
                           competitions=competitions, 
                           teams=teams 
                           )

@bp.route('/add_competition', methods=('GET', 'POST'))
def add_competition():
    db = get_db()
    if request.method == "POST":
        try:
            db.execute(
                "INSERT INTO competitions (name, season) VALUES (?, ?)",
                (request.form.get("competition"), request.form.get("season")),
            )
            db.commit()
        except db.IntegrityError:
            flash("Error")
    
    return redirect(url_for("admin.index"))


@bp.route('/add_team', methods=('GET', 'POST'))
def add_team():
    db = get_db()
    if request.method == "POST":
        try:
            db.execute(
                "INSERT INTO teams (name) VALUES (?)",
                (request.form.get("team"),)
            )
            db.commit()
        except db.IntegrityError:
            flash("Team already exists")

    return redirect(url_for("admin.index"))

@bp.route('/add_match', methods=('GET', 'POST'))
def add_match():
    db = get_db()
    if request.method == "POST":
        competition = request.form.get("competition")
        home_team = request.form.get("home_team")
        away_team = request.form.get("away_team")
        datetime = request.form.get("datetime")
        try:
            db.execute(
                "INSERT INTO matches (competition_id," \
                "   home_team_id, away_team_id, match_date)" \
                "   VALUES (?, ?, ?, ?)",
                (competition, home_team, away_team, datetime)
            )
            db.commit()
        except db.IntegrityError:
            flash("Invalid input")

    return redirect(url_for("admin.index"))

@bp.route('/<int:competition_id>/matches')
@admin_required
def matches(competition_id):
    matches = get_db().execute(
        """
                SELECT matches.id,
                    competitions.name AS competitions,
                    competitions.season,
                    home.name AS home_team,
                    away.name AS away_team,
                    matches.home_score,
                    matches.away_score,
                    matches.match_date,
                    matches.status
                FROM matches
                JOIN competitions ON competitions.id = matches.competition_id
                JOIN teams AS home
                    ON home.id = matches.home_team_id
                JOIN teams AS away
                    ON away.id = matches.away_team_id
                WHERE matches.competition_id = ?
                ORDER BY matches.match_date
            """,
            (competition_id,)
    )
    return render_template("admin/matches.html", matches=matches)
