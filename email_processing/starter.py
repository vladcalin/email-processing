from importlib.machinery import SourceFileLoader
import json


class ConfigurationProvider:
    def __init__(self, configuration_file=None):
        if configuration_file:
            try:
                self.config = SourceFileLoader("email_processing.settings", configuration_file).load_module()
            except ImportError:
                raise
        else:
            import email_processing.settings
            self.config = email_processing.settings

    def get_broker_url(self):
        redis_password = self.config.REDIS.get("password", None)
        redis_host = self.config.REDIS.get("host", "127.0.0.1")
        redis_port = self.config.REDIS.get("port", 6379)
        redis_db = self.config.REDIS.get("db", 0)
        return "redis://" + \
               ((":" + redis_password + "@") if redis_password else "") + \
               redis_host + ":" + str(redis_port) + "/" + str(redis_db)

    def get_backend_url(self):
        pg_user = self.config.POSTGRESQL["username"]
        pg_password = self.config.POSTGRESQL["password"]
        pg_host = self.config.POSTGRESQL.get("host", "127.0.0.1")
        pg_port = self.config.POSTGRESQL.get("port", 5432)
        pg_db = self.config.POSTGRESQL.get("database", "email_processing")
        return "db+postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}".format(
            username=pg_user, password=pg_password, host=pg_host, port=pg_port, database=pg_db
        )
