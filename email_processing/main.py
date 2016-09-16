from importlib.machinery import SourceFileLoader
import json
import subprocess
import os
import argparse
import sys

from email_processing.settings import RUNTIME_CONFIG
from email_processing.models import assure_tables


class ConfigurationProvider:
    def __init__(self, configuration_file):
        self.config = SourceFileLoader("email_processing.user_settings", configuration_file).load_module()

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

    def write_final_config(self):
        final_settings = {
            "broker": self.get_broker_url(),
            "backend": self.get_backend_url(),
            "inboxes": self.config.INBOXES
        }
        with open(RUNTIME_CONFIG, "w") as final_conf_fp:
            json.dump(final_settings, final_conf_fp)


class Starter:
    def __init__(self, config_file_path, workers, concurrency):
        self.config_file_path = config_file_path
        self._workers = []
        self._worker_count = workers
        self._concurrency = concurrency

    def start_celery_workers(self):
        for _ in range(self._worker_count):
            worker_proc_cmd = '"{python}" -m celery worker -A email_processing.core --concurrency={conc} -l DEBUG'.format(
                python=sys.executable, conc=self._concurrency
            )
            worker_proc = subprocess.Popen(worker_proc_cmd)
            self._workers.append(worker_proc)

    def start_celery_beat(self):
        pass

    def hang(self):
        for proc in self._workers:
            proc.wait()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("config_file", help="The configuration file required for the application to run")
    parser.add_argument("--workers", help="The number of workers to process tasks. Defaults to 1", default=1,
                        type=int)
    parser.add_argument("--concurrency",
                        help="The number of tasks to process simultanously by each worker. Defaults to 3",
                        type=int, default=3)

    args = parser.parse_args(sys.argv[1:])

    config_provider = ConfigurationProvider(args.config_file)
    config_provider.write_final_config()
    assure_tables()

    starter = Starter(RUNTIME_CONFIG, workers=args.workers, concurrency=args.concurrency)
    starter.start_celery_workers()
    starter.start_celery_beat()

    starter.hang()
