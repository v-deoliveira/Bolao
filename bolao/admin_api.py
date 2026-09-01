from flask import(
    Blueprint, flash, redirect, render_template, request, url_for
)
from .db import get_db
from .admin import admin_required
from .football_api import(
    get_competitions, get_matches, get_areas
)
import requests

bp = Blueprint('admin_api', __name__, url_prefix='/admin_api')

@bp.route('/sync', methods=('POST',))
@admin_required
def sync():
    #Will request the API's competitions, and from it grab the 'areas' data.
    #Two except blocks. They will not collide, because each handles a very distinc error type.
    try:
        response = get_competitions()
        areas = get_areas(response)
    except requests.exceptions.RequestException as e:
        flash(f"Could not reach the API: {e}")
        return redirect(url_for("admin.index"))
    except KeyError as e:
        flash(f"Unexpect API response - a competition is missing a field: {e}")
        return redirect(url_for("admin.index"))

    return areas