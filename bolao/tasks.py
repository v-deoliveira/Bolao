from .football_api import sync_results
from .db import get_db

# I need to use app.app_context here, so for this I have to pass 'app' into the function.
def update_results(app):
    with app.app_context():
        db = get_db()
        try:
            sync_results()
            db.commit()
            app.logger.info("Results synced.")
        except Exception:
            db.rollback()
            app.logger.exception("Error syncing results.")