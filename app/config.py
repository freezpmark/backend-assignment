import os


def get_db_uri():
    return "{}://{}:{}@{}:{}/{}".format(
    os.getenv("db_protocol"),
    os.getenv("db_user"),
    os.getenv("db_password"),
    os.getenv("db_host"),
    os.getenv("db_port"),
    os.getenv("db_name"),
)
