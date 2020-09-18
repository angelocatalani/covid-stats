import datetime
import logging

from prometheus_client import start_http_server
from environs import Env

from covid_stats.core import Exporter
from covid_stats.core import scraper

START_DATE = datetime.date(2020,1,1)
INFLUXDB_NAME = "covid_stats_by_country"
BATCH_SIZE = 512


if __name__ == "__main__":
    logging.basicConfig(
        level="DEBUG",
        datefmt="%H:%M:%S",
        format="[%(asctime)s] %(name)s - %(threadName)s - %(levelname)s: %(message)s",
    )
    logger = logging.getLogger(__name__)
    env = Env()
    env.read_env("../covid_stats.env")
    start_http_server(env.int("PROMETHEUS_APP_PORT"))

    exporter = Exporter(host=env.str("INFLUXDB_HOST"), port=env.int("INFLUXDB_PORT"))

    country_data = scraper.retrieve_all_countries_data(start_date=START_DATE,end_date=datetime.datetime.now().date())
    logger.info(f"completed data retrieval")

    exporter.write(data=country_data,database=INFLUXDB_NAME,batch_size=BATCH_SIZE)
    logger.info(f"exported data to InfluxDB: {INFLUXDB_NAME}")
