from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from .db import get_db
from .admin import admin_required

bp = Blueprint('admin_tournaments', __name__, url_prefix='/admin_tournaments')

@bp.route('/', methods=('GET', 'POST'))
@admin_required
def manage_tournaments():
    db = get_db()

    tournaments = db.execute(
        "SELECT * FROM competitions"
    ).fetchall()

    return render_template("admin/tournaments.html", tournaments=tournaments)