import argparse
import datetime
import logging
import time

import schedule
from environs import Env
from prometheus_client import start_http_server

from covid_stats.core import Exporter, scraper

START_DATE = datetime.date(2020, 1, 1)
INFLUXDB_NAME = "covid_stats_by_country"
BATCH_SIZE = 512
ONE_HOUR = 60 * 60
logging.basicConfig(
    level="INFO",
    datefmt="%H:%M:%S",
    format="[%(asctime)s] %(name)s - %(threadName)s - %(levelname)s: %(message)s",
)


def init_database() -> None:
    """
    Entry point to initialize the database with Covid stats.
    """

    logger = logging.getLogger(__name__)
    env = Env()
    env.read_env("../covid_stats.env")

    exporter = Exporter(host=env.str("INFLUXDB_HOST"), port=env.int("INFLUXDB_PORT"))

    country_data = scraper.retrieve_all_countries_data(
        start_date=START_DATE, end_date=datetime.datetime.now().date()
    )
    logger.info(f"completed historical data retrieval")

    exporter.write(data=country_data, database=INFLUXDB_NAME, batch_size=BATCH_SIZE)
    logger.info(f"exported historical data to InfluxDB: {INFLUXDB_NAME}")


def real_time() -> None:
    """
    Entry point to retrieve real-time Covid stats.
    """
    logger = logging.getLogger(__name__)
    env = Env()
    env.read_env("../covid_stats.env")
    start_http_server(env.int("PROMETHEUS_PORT"))
    exporter = Exporter(host=env.str("INFLUXDB_HOST"), port=env.int("INFLUXDB_PORT"))

    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
    today = datetime.datetime.now().date()
    country_data = scraper.retrieve_all_countries_data(start_date=yesterday, end_date=today)
    logger.info(f"completed data retrieval for {yesterday}")
    exporter.write(data=country_data, database=INFLUXDB_NAME, batch_size=BATCH_SIZE)
    logger.info(f"exported {yesterday} data to InfluxDB: {INFLUXDB_NAME}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "entrypoint",
        choices=["init_database", "real_time"],
        help="initialize the database or start retrieving real time data",
        type=str,
    )
    entrypoint = parser.parse_args().entrypoint
    if entrypoint == "init_database":
        init_database()
    else:
        schedule.every().day.do(real_time)
        while True:
            schedule.run_pending()
            time.sleep(ONE_HOUR)
