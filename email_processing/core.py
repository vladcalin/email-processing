import json
import sys
import argparse
import importlib
import json

from celery import Celery
from celery.schedules import crontab

from email_processing.settings import RUNTIME_CONFIG

with open(RUNTIME_CONFIG, "r") as json_conf:
    config = json.load(json_conf)


def get_periodic_tasks():
    tasks = {}


app = Celery(
    'email_processing.core',
    broker=config["broker"],
    backend=config["backend"],
    include=[
        "email_processing.default_tasks",
        "email_processing.periodic_tasks"
    ]
)

app.conf.update(
    BROKER_URL=config["broker"],
    CELERY_RESULT_BACKEND=config["backend"],

    CELERY_TASK_SERIALIZER="json",
    CELERY_RESULT_SERIALIZER="json",
    CELERY_ACCEPT_CONTENT=["json"],
    CELERY_RESULT_DB_TABLENAMES={
        'task': 'processed_tasks',
        'group': 'myapp_groupmeta',
    },
    CELERYBEAT_SCHEDULE=get_periodic_tasks()
)

if __name__ == '__main__':
    app.start()
