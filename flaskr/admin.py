from functools import wraps

from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db

from .helpers import calculate_points

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

    tournaments = db.execute(
        """
            SELECT * FROM tournaments
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
                           tournaments=tournaments, 
                           teams=teams 
                           )

@bp.route('/add_match', methods=('GET', 'POST'))
@admin_required
def add_match():
    db = get_db()
    if request.method == "POST":
        tournament = request.form.get("tournament")
        home_team = request.form.get("home_team")
        away_team = request.form.get("away_team")
        datetime = request.form.get("datetime")
        try:
            db.execute(
                "INSERT INTO matches (tournament_id," \
                "   home_team_id, away_team_id, match_date)" \
                "   VALUES (?, ?, ?, ?)",
                (tournament, home_team, away_team, datetime)
            )
            db.commit()
        except db.IntegrityError:
            flash("Invalid input")

    return redirect(url_for("admin.index"))

@bp.route('/tournament/<int:tournament_id>/matches')
@admin_required
def matches(tournament_id):
    db = get_db()

    tournament = db.execute(
        """
            SELECT name, season
            FROM tournaments
            WHERE id = ?
        """,
        (tournament_id,)
    ).fetchone()

    matches = db.execute(
        """
            SELECT matches.id,
                home.name AS home_team,
                away.name AS away_team,
                matches.home_score,
                matches.away_score,
                matches.match_date,
                matches.status_finished
            FROM matches
            JOIN teams AS home
                ON home.id = matches.home_team_id
            JOIN teams AS away
                ON away.id = matches.away_team_id
            WHERE matches.tournament_id = ?
            ORDER BY matches.match_date
        """,
        (tournament_id,)
    ).fetchall() #Was getting a bug because forgot fetchall()

    return render_template("admin/matches.html", matches=matches, 
                                                 tournament=tournament,
                                                 tournament_id=tournament_id)

@bp.route('/tournament/<int:tournament_id>/match/<int:match_id>/edit_match', methods=('GET', 'POST'))
@admin_required
def edit_match(tournament_id, match_id):
    db = get_db()
    if request.method == "POST":
        try:
            home_score = int(request.form.get("home_score"))
            away_score = int(request.form.get("away_score"))
        except ValueError:
            flash("Invalid input. Must be a positive number.")
            return redirect(url_for("admin.edit_match", tournament_id=tournament_id, match_id=match_id))
        # Checks for a positive int
        if home_score < 0 or away_score < 0:
            flash("Score must be positive")
            return redirect(url_for("admin.edit_match", tournament_id=tournament_id, match_id=match_id))

        status_finished = 1
        db.execute(
            """
                UPDATE matches
                SET home_score = ?,
                    away_score = ?,
                    status_finished = ?
                WHERE id = ?
            """,
            (home_score, away_score, status_finished, match_id)
        )
        db.commit()

        predictions = db.execute(
            """
                SELECT id, home_score, away_score
                FROM predictions
                WHERE match_id = ?
            """,
            (match_id,)
        ).fetchall()

        for p in predictions:
            pts = calculate_points(home_score, away_score, p["home_score"], p["away_score"])
            db.execute(
                """
                    UPDATE predictions
                    SET points = ?
                    WHERE id = ?
                """,
                (pts, p["id"])
            )
            db.commit()

        return redirect(url_for("admin.matches", tournament_id=tournament_id))
    
    match = db.execute(
        """
            SELECT home.name AS home_team,
                away.name AS away_team,
                matches.home_score,
                matches.away_score,
                matches.match_date,
                matches.status_finished
            FROM matches
            JOIN teams AS home
                ON home.id = matches.home_team_id
            JOIN teams AS away
                ON away.id = matches.away_team_id
            WHERE matches.id = ?
        """,
        (match_id,)
    ).fetchone()
    
    return render_template("admin/edit.html", match=match)