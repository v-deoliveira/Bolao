from flask import(
    Blueprint, flash, redirect, render_template, request, url_for
)
from .db import get_db
from .admin import admin_required
from .helpers import delete_helper

bp = Blueprint('admin_teams', __name__, url_prefix='/admin_teams')

TABLE_NAME = "teams"

@bp.route('/', methods=('GET', 'POST'))
@admin_required
def index():
    db = get_db()
    teams = db.execute(
        "SELECT * FROM teams"
    ).fetchall()
    return render_template("admin/teams.html", teams=teams)

@bp.route('/create', methods=('POST',))
@admin_required
def create():
    db = get_db()
    team = request.form.get("team")
    # No try/except for now, because no rules set yet in the databse for team creation .eg UNIQUE
    if team is not None:
       db.execute(
           "INSERT INTO teams (name) VALUES (?)", (team,)
       )
       db.commit()
       flash(f"{team} created")   
    return redirect(url_for("admin_teams.index"))

@bp.route('/<int:id>/delete', methods=('POST',))
@admin_required
def delete(id):
    db = get_db()
    # First check for a valid team_id. Then if delete_helper fails, team is being used.
    check_id = db.execute(
        "SELECT id FROM teams WHERE id = ?", (id,)
    ).fetchone()
    if not check_id:
        error = "ERROR - INVALID TEAM"
        return redirect(url_for("admin_teams.index"))

    flash("Team Deleted") if delete_helper(id, TABLE_NAME) else flash("ERROR - TEAM BEING USED")
    return redirect(url_for("admin_teams.index"))