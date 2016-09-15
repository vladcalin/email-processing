import json
import sys
import argparse
import importlib

from celery import Celery

import email_processing.settings as default_settings







app = Celery(
    'email_processing.core',
    broker=config.get_broker_url(),
    backend=config.get_backend_url(),
    include=[
        "email_processing.email_processing_tasks",
        "email_processing.periodic_tasks"
    ]
)

app.conf.update(
    BROKER_URL=config.get_broker_url(),
    CELERY_RESULT_BACKEND=config.get_backend_url(),

    CELERY_TASK_SERIALIZER="json",
    CELERY_RESULT_SERIALIZER="json",
    CELERY_ACCEPT_CONTENT=["json"],
    CELERY_RESULT_DB_TABLENAMES={
        'task': 'processed_tasks',
        'group': 'myapp_groupmeta',
    }
)

if __name__ == '__main__':
    app.start()
