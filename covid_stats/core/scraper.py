"""Utility to fetch and manipulate  COVID-19 data."""


import datetime
import logging
from typing import Any, Dict, List

import requests
from tenacity import RetryError, retry, retry_if_exception_type, stop_after_attempt, stop_after_delay, wait_random

logger = logging.getLogger(__name__)

class ApiError(Exception):
    """
    The Covid API failed.
    """

def convert_date_to_string(start_date: datetime.date) -> str:
    """
    Convert date object to string in zulu timezone.

    :param start_date: the date to convert
    """
    return start_date.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_all_countries() -> List[str]:
    """
    Get all the countries to retrieve stats.
    :return: the country to retrieve data
    """
    url = "https://api.covid19api.com/countries"
    response = requests.request("GET", url, headers={}, data={}).json()
    countries = [item["Slug"] for item in response if item["Slug"]!="united-states" ]
    return countries

@retry(retry=retry_if_exception_type(ApiError),wait=wait_random(1,2),stop=(stop_after_delay(30)))
def retrieve_country_data(
    country: str, start_date: datetime.date, end_date: datetime.date
) -> List[Dict[str, Any]]:
    """
    Retrieve cumulative stats by country.
    Data is formatted according to the InfluxDB specifications.

    :param country: the country to get stats
    :param start_date: the inclusive starting date to get stats
    :param end_date: the inclusive ending date to get stats
    :return: the stats data formatted according to the InfluxDB specifications
    """
    start_date_string = convert_date_to_string(start_date)
    end_date_string = convert_date_to_string(end_date)

    url = f"https://api.covid19api.com/country/{country}?from={start_date_string}&to={end_date_string}"
    try:
        response = requests.get(url, headers={}, data={},stream=True).json()
    except requests.exceptions.RequestException :
        logger.warning(f'network error retrieving country: {country} from {start_date_string} to {end_date_string}')
        raise ApiError(f'network error retrieving country: {country} from {start_date_string} to {end_date_string}')

    if "success" in response and not response["success"]:
        logger.warning(f"{response} retrieving data for country: {country} from {start_date_string} to {end_date_string}")

        raise ApiError(response)
    formatted_data = []
    for item in response:
        formatted_item = {
            "measurement": "country_data",
            "time": item["Date"],
            "tags": {
                "country": item["Country"],
            },
            "fields": {
                "confirmed": item["Confirmed"],
                "deaths": item["Deaths"],
                "recovered": item["Recovered"],
            },
        }

        formatted_data.append(formatted_item)

    return formatted_data


def retrieve_all_countries_data(
    start_date: datetime.date, end_date: datetime.date
) -> List[Dict[str, Any]]:
    """
    Retrieve cumulative stats for all countries.
    Data is formatted according to the InfluxDB specifications.

    :param start_date: the inclusive starting date to get stats
    :param end_date: the inclusive ending date to get stats
    :return: the stats data formatted according to the InfluxDB specifications
    """

    countries = get_all_countries()
    all_countries = len(countries)
    i = 1
    all_countries_data = []
    for country in countries:
        logger.info(f"start retrieving data for {i}/{all_countries}-th country: {country} from {start_date} to {end_date}")

        try:
            country_data = retrieve_country_data(
                country=country, start_date=start_date, end_date=end_date
            )
            logger.info(
                f"successful data retrieval for {i}/{all_countries}-th country: {country} from {start_date} to {end_date}")
            all_countries_data.extend(country_data)
            i+=1
        except RetryError:
            logger.warning(
                f"skipping {i}/{all_countries}-th country: {country} from {start_date} to {end_date} because retried too many times")

    return all_countries_data
