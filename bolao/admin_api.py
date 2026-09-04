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

    try:
        db = get_db()
        for area in areas:
            db.execute(
                """
                    INSERT INTO areas (code, name, id, flag) VALUES (?, ?, ?, ?)
                    ON CONFLICT (id) DO NOTHING
                """,
                (area.get("code"), area.get("name"), area.get("id"), area.get("flag")),
                #Using .get() here for handle not only missing necessary values, but also any missing key.
            )
        db.commit()
        flash("All areas synced")
        return redirect(url_for("admin.index"))
    except db.IntegrityError as e:
        flash(f"The API's response is missing data: {e}")
        return redirect(url_for("admin.index"))
