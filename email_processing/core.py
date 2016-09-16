import json
import sys
import argparse
import importlib
import json

from celery import Celery
from celery.schedules import crontab

from email_processing.settings import RUNTIME_CONFIG
from email_processing.models import Session, Inbox

with open(RUNTIME_CONFIG, "r") as json_conf:
    config = json.load(json_conf)


def get_periodic_tasks():
    tasks = {}
    # clearing all old inboxes
    session = Session()
    session.query(Inbox).delete()
    session.commit()

    session = Session()
    for inbox in config["inboxes"]:
        inbox_instance = Inbox()

        inbox_instance.id = inbox["id"]
        inbox_instance.host = inbox["host"]
        inbox_instance.port = inbox["port"]
        inbox_instance.protocol = inbox["protocol"]
        inbox_instance.use_ssl = inbox["use_ssl"]
        inbox_instance.username = inbox["username"]
        inbox_instance.password = inbox["password"]

        session.add(inbox_instance)

        frequency_cron = inbox["frequency"]
        on_result = inbox["on_result"]
        on_error = inbox["on_error"]

        tasks["periodic_process_{}".format(inbox_instance.id)] = {
            "task": "email_processing.default_tasks.process_inbox",
            "schedule": crontab(frequency_cron),
            "kwargs": {
                "id": inbox_instance.id,
                "host": inbox_instance.host,
                "port": inbox_instance.port,
                "protocol": inbox_instance.protocol,
                "use_ssl": inbox_instance.use_ssl,
                "username": inbox_instance.username,
                "password": inbox_instance.password,
                "on_result": on_result,
                "on_error": on_error
            }
        }
    session.commit()
    return tasks


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
