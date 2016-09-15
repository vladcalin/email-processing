from email_processing.core import app


@app.task
def retrieve_emails_pop(host, port, username, password, use_ssl=True):
    pass

