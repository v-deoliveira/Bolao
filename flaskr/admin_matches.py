from flask import(
    Blueprint, flash, jsonify, redirect, render_template, request, url_for
)
from .db import get_db
from .admin import admin_required
from .helpers import calculate_points, delete_helper

bp = Blueprint('admin_matches', __name__, url_prefix='/admin_matches')

TABLE_NAME = "matches"

@bp.route('/', methods=('GET', 'POST'))
@admin_required
def index():
    db = get_db()
    tournaments = db.execute(
        "SELECT * FROM tournaments ORDER BY name, season"
    ).fetchall() 
    teams = db.execute(
        "SELECT * FROM teams ORDER BY name"
    ).fetchall()

    selected_tournament = None
    matches = None
    selected_tournament_id = request.args.get("tournament_id")
    if selected_tournament_id is not None:
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
            (selected_tournament_id,)
        ).fetchall()

        selected_tournament = db.execute(
            "SELECT name, season FROM tournaments WHERE id = ?",
            (selected_tournament_id,)
        ).fetchone()

    return render_template("admin/matches.html", tournaments=tournaments,
                                                 teams=teams,
                                                 matches=matches,
                                                 selected_tournament=selected_tournament
                                                 )

@bp.route('/create', methods=('POST',))
@admin_required
def create():
    db = get_db()
    tournament_id = request.form.get("tournament")
    home_id = request.form.get("home_team")
    away_id = request.form.get("away_team")
    match_date = request.form.get("datetime")
    if match_date is None:
        flash("Missing Match Date")
    else:
        try:
            db.execute(
                """
                    INSERT INTO matches 
                    (tournament_id, home_team_id, away_team_id, match_date) 
                    VALUES (?, ?, ?, ?)
                """,
                (tournament_id, home_id, away_id, match_date)
            )
            db.commit()
            flash("Match Created")
        except db.IntegrityError:
            flash("ERROR - INVALID INPUT")

    return redirect(url_for("admin_matches.index"))

@bp.route('/<int:match_id>/edit', methods=('GET', 'POST'))
@admin_required
def edit(match_id):
    db = get_db()
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

    if request.method == 'POST':
        # Makes sure the input will be an int
        try:
            home_score = int(request.form.get("home_score"))
            away_score = int(request.form.get("away_score"))
        except ValueError:
            flash("Invalid input. Must be a positive number.")
            return redirect(url_for("admin.edit_match", match_id=match_id))
        # Then check for a positive int
        if home_score < 0 or away_score < 0:
            flash("Score must be positive")
            return redirect(url_for("admin.edit_match", match_id=match_id))

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

        # Update predictions points
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
        flash("Match Updated")
        return redirect(url_for("admin_matches.index"))
    
    return render_template("admin/edit.html", match=match)

@bp.route('/<int:match_id>/delete', methods=('POST',))
@admin_required
def delete(match_id):
    flash("Match deleted") if delete_helper(match_id, TABLE_NAME) else flash("ERROR - FAILED TO DELETE MATCH")
    return redirect(url_for("admin_matches.index"))