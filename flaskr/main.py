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
    return render_template("main/index.html")

@bp.route('/matches', methods=('GET', 'POST'))
@login_required
def matches():
    db = get_db()

    competitions = db.execute(
        """
            SELECT * FROM competitions
        """
    ).fetchall()

    matches = db.execute(
        """
            SELECT * FROM matches
            WHERE competition_id = ?
        """,
        (request.args.get("competition"),)
    ).fetchall()

    return render_template("main/matches.html", competitions=competitions, matches=matches)