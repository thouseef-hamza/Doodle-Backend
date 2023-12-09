from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "doodle.settings")
app = Celery("doodle")
app.conf.enable_utc = False
app.conf.update(timezone="Asia/Kolkata")
app.config_from_object(settings, namespace="CELERY")

# Celery Beat
app.conf.beat_schedule = {
    "task-for-batch-student-fees-email": {
        "task": "payments.tasks.send_student_fees_to_email",
        "schedule": crontab(day_of_month="1-15", hour=9, minute=30),
    },
    "task-for-batch-student-fees-overdue-email":{
        "task":"payments.tasks.send_student_fees_overdue_email",
        "schedule":crontab(day_of_month="1-15",hour=9,minute=30)
    },
    "task-for-batch-student-fees-overdue-penalty":{
        "task":"payments.tasks.student_fees_overdue_penalty",
        "schedule":crontab(day_of_month="*",hour=9,minute=30)
    }
}


app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
