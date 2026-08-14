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