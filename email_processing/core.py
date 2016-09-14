from celery import Celery

app = Celery(
    'email_processing.core',
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=[
        "email_processing.email_processing_tasks",
        "email_processing.periodic_tasks"
    ]
)

app.conf.update(
    BROKER_URL="redis://localhost:6379/0",
    CELERY_RESULT_BACKEND="redis://localhost:6379/1",

    CELERY_TASK_SERIALIZER="json",
    CELERY_RESULT_SERIALIZER="json",
    CELERY_ACCEPT_CONTENT=["json"]
)

if __name__ == '__main__':
    app.start()
