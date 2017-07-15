from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger

from alugueme.views import check_due_date

logger = get_task_logger(__name__)

@periodic_task(
        #run_every=(crontab(hour=0, minute=0)),
        run_every=(crontab(minute='*/1')),
        name="check_due_date_task",
        ignore_result=True)
def check_due_date_task():
    """Checks for items due date"""
    check_due_date()
    logger.info("Checked items due date")
