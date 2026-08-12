from flask import(
    Blueprint, flash, redirect, render_template, request, url_for
)
from .db import get_db
from .admin import admin_required

bp = Blueprint('admin_tournaments', __name__, url_prefix='/admin_tournaments')

@bp.route('/', methods=('GET', 'POST'))
@admin_required
def index():
    db = get_db()

    tournaments = db.execute(
        "SELECT * FROM tournaments"
    ).fetchall()
    return render_template("admin/tournaments.html", tournaments=tournaments)

@bp.route('/create', methods=('POST',))
@admin_required
def create():
    db = get_db()
    tournament = request.form.get("tournament")
    season = request.form.get("season")

    if tournament is not None and season is not None:
        try:
            db.execute(
                "INSERT INTO tournaments (name, season) VALUES (?, ?)",
                (tournament, season),
            )
            db.commit()
            flash("Tournament created")
        except db.IntegrityError:
            flash("ERROR - Tournament already exists")
    return redirect(url_for("admin_tournaments.index"))

# The html form will pass the tournament_id as 'id'to this route
@bp.route('/<int:id>/delete', methods=('POST',))
@admin_required
def delete(id):
    db = get_db()
    try:
        db.execute(
            "DELETE FROM tournaments WHERE id = ?", (id,)
        )
        db.commit()
        flash("Tournament deleted")
    except db.IntegrityError:
        flash("ERROR - Failed to delete tournament.")

    return redirect(url_for("admin_tournaments.index"))