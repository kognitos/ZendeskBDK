"""
A short description of the project.
"""
import logging
from typing import Optional
from urllib.parse import quote

import requests
from kognitos.bdk import autoconvert, procedure, book, connect
from kognitos.bdk.concept import NounPhrase

OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
DEFAULT_TIMEOUT = 30

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@book(icon="data/icon.svg")
class OpenWeatherBook:
    """
    A book for A short description of the project.

    Author:
      Your Name
    """

    def __init__(self):
        """
        Initializes an instance of the class.

        :param self: The instance of the class.
        """
        self._base_url = OPENWEATHER_BASE_URL
        self._api_key = None
        self._timeout = float(DEFAULT_TIMEOUT)

    @property
    def timeout(self) -> float:
        """
        Get the value of the timeout.

        Parameters:
            None

        Returns:
            The value of the timeout.

        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: float):
        """Sets the timeout value in milliseconds.

        Args:
            timeout (int): The timeout value to set. Must be a positive integer.

        Raises:
            ValueError: If the timeout value is less than or equal to 0.

        """
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self._timeout = timeout

    @connect
    def connect(self, api_key: str):
        """
        Connects to an API using the provided API key.

        Arguments:
            api_key: The API key to be used for connecting

        Labels:
            api_key: API Key
        """
        test_url = f"{self._base_url}?appid={api_key}&q=London"
        response = requests.get(test_url, timeout=self._timeout)
        if response.status_code == 401:
            response_data = response.json()
            if "Invalid API key" in response_data.get("message", ""):
                raise ValueError("Invalid API key")

        self._api_key = api_key

    @autoconvert
    @procedure("to get the current temperature at a city")
    def current_temperature(self, city: NounPhrase) -> Optional[float]:
        """Fetch the current temperature for a specified city.

        Args:
            city (str): The name of the city.

        Returns:
            Optional[float]: The current temperature in Celsius, or None if an error occurs.
        """
        complete_url = f"{self._base_url}?appid={self._api_key}&q={quote(city.to_string())}&units=metric"
        try:
            response = requests.get(complete_url, timeout=self._timeout)
            weather_data = response.json()
            if weather_data["cod"] == 200:
                temperature = weather_data["main"]["temp"]
                return temperature

            logger.error(
                "error fetching data for %s, response Code: %s", city.to_string(), weather_data['cod']
            )
            return None
        except requests.Timeout:
            logger.error("request timed out")
            return None
        except requests.RequestException as e:
            logger.error("error occurred: %s", e)
            return None
