from email_processing.core import app


@app.task
def add(a, b):
    return a + b


@app.task
def multiply(a, b):
    return a * b


@app.task
def power(a, b):
    return a ** b
