from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return 'Main page'