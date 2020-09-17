from typing import Any, Dict, List

from influxdb import InfluxDBClient


class Exporter:
    """
    Export data to the InfluxDB.
    """

    def __init__(self, host: str, port: int):
        """
        Create the InfluxDB client.

        :param host: the database ip address
        :param port: the database port number
        """
        self._client = InfluxDBClient(host=host, port=port)

    def create_db(self,database: str)->None:
        """
        Create an empty database.

        :param database: the database name
        """
        self._client.create_database(database)


    def write(self, database: str, data: List[Dict[str, Any]], batch_size: int) -> None:
        """
        Initialize and write to the database.

        :param database: the database name
        :param data: the json data to write
        :param batch_size: the batch size
        """
        self._client.create_database(database)
        self._client.write_points(points=data, batch_size=batch_size,database=database)
