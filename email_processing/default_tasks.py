from email_processing.core import app


@app.task
def process_inbox(host, port, protocol, use_ssl, username, password, on_result, on_error):
    pass


