from flask import(
    Blueprint, flash, redirect, render_template, request, url_for
)
from .db import get_db
from .admin import admin_required
from .football_api import(
    get_competitions, get_matches, get_areas, get_teams, create_matches
)
import requests

bp = Blueprint('admin_api', __name__, url_prefix='/admin_api')

@bp.route('/sync', methods=('POST',))
@admin_required
def sync():
    db = get_db()
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

    # I choose to use distinct try/except here, for better code maintance. In case of errors, is easy to catch where is it.
    try:
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
    except db.IntegrityError as e:
        flash(f"The API's response is missing data: {e}")
        return redirect(url_for("admin.index"))

    try:
        for comp in response:
            # PERHAPS NEED A CHECK FOR MISSING ID, BECAUSE INTEGRITYERROR WILL NOT CATCH IT, AND THE INSERT WILL FAIL SILENTLY.
            db.execute(
                """
                    INSERT INTO tournaments (id, area_id, name, code, type, emblem) VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT (id) DO NOTHING
                """,
                (comp.get("id"), comp.get("area", {}).get("id"), comp.get("name"), comp.get("code"), comp.get("type"), comp.get("emblem")),
                # Add to .get("area") default value of {}, cuase if .get("area") returns None, .get("id") wont break and throw unexpected error.
            )

            # If currentSeason is missing, raise KeyError, because db.IntegrityError will not catch it.
            current_season = comp.get("currentSeason")
            if current_season is None:
                raise KeyError(f"Competition {comp.get('name')} has no currentSeason")
            
            db.execute(
                """
                    INSERT INTO seasons (tournament_id, end_date, id, start_date) VALUES (?, ?, ?, ?)
                    ON CONFLICT (id) DO NOTHING
                """,
                (comp.get("id"), current_season.get("endDate"), current_season.get("id"), current_season.get("startDate")),
            )
        db.commit()
        flash("All competitions and seasons synced")
    except (db.IntegrityError, KeyError) as e:
        flash(f"The API's response is missing data: {e}")
        return redirect(url_for("admin.index"))

    return redirect(url_for("admin.index"))


# This route will first sync all teams from the selected competition, and then sync the matches.
# We first need the teams, because the matches table references the teams id on the teams table.
@bp.route('/<int:id>/sync_matches', methods=('POST',))
@admin_required
def sync_matches(id):
    db = get_db()
    try:
        get_teams(id)
        matches = get_matches(id)
        create_matches(matches)
        db.commit()
        flash("Teams and matches synced")
    except requests.exceptions.RequestException as e:
        flash(f"Could not reach the API: {e}")
        return redirect(url_for("admin_tournaments.index"))
    except (db.IntegrityError, KeyError) as e:
        flash(f"The API's response is missing data: {e}")
        return redirect(url_for('admin_tournaments.index'))

    return redirect(url_for('admin_tournaments.index'))

@bp.route('/test', methods=('GET', 'POST'))
@admin_required
def test():
    id = '2000'
    data = get_matches(id)
    return data