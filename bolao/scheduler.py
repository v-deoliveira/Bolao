from apscheduler.schedulers.background import BackgroundScheduler
from .tasks import update_results

scheduler = BackgroundScheduler(timezone="UTC")

# this is the function that will be called in __init.py__ to start the scheduler.
# I need to pass 'app' to the function and also as an argument to update_results, because I need to use app.app_context() inside the function, so I can access the database.
def init_scheduler(app):
    scheduler.add_job(update_results, 'interval', minutes=1, args=[app], id='update_results', replace_existing=True)
    scheduler.start()
