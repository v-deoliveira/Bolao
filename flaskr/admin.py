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
    return "Admin Panel"