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

@bp.route('/')
@admin_required
def index():
    competitions = get_db().execute(
        "SELECT * FROM competitions"
    ).fetchall()
    
    teams = get_db().execute(
        "SELECT * FROM teams"
        "   ORDER BY name"
    ).fetchall()

    return render_template("admin/admin.html", competitions=competitions, teams=teams)

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


@bp.route('add_team', methods=('GET', 'POST'))
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