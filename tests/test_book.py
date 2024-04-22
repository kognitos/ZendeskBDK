# pylint: disable=missing-module-docstring, missing-function-docstring
import pytest
import requests_mock
from kognitos.bdk.concept import NounPhrase

from openweather import OPENWEATHER_BASE_URL, OpenWeatherBook

API_KEY = "test_api_key"


@pytest.fixture
def openweather_book():
    book = OpenWeatherBook()
    return book


def test_api_key_valid(openweather_book):
    with requests_mock.Mocker() as m:
        m.get(
            f"{OPENWEATHER_BASE_URL}?appid={API_KEY}&q=London",
            status_code=200,
        )
        openweather_book.connect(API_KEY)


def test_api_key_invalid(openweather_book):
    with requests_mock.Mocker() as m:
        m.get(
            f"{OPENWEATHER_BASE_URL}?appid={API_KEY}&q=London",
            status_code=401,
            json={"message": "Invalid API key"},
        )
        with pytest.raises(ValueError):
            openweather_book.connect(API_KEY)


def test_current_temperature(openweather_book):
    with requests_mock.Mocker() as m:
        m.get(
            f"{OPENWEATHER_BASE_URL}?appid={API_KEY}&q=London",
            status_code=200,
        )
        m.get(
            f"{OPENWEATHER_BASE_URL}?q=New%20York&appid={API_KEY}&units=metric",
            json={"cod": 200, "main": {"temp": 20.0}},
        )
        openweather_book.connect(API_KEY)
        temperature = openweather_book.current_temperature(NounPhrase("New York", []))
        assert temperature == 20.0, "The temperature should be 20.0°C"


def test_get_current_temperature_error_response(openweather_book):
    with requests_mock.Mocker() as m:
        m.get(
            f"{OPENWEATHER_BASE_URL}?appid={API_KEY}&q=London",
            status_code=200,
        )
        m.get(
            f"{OPENWEATHER_BASE_URL}?q=NonExistentCity&appid={API_KEY}&units=metric",
            json={"cod": 404, "message": "city not found"},
            status_code=404,
        )
        openweather_book.connect(API_KEY)
        temperature = openweather_book.current_temperature(
            NounPhrase("NonExistentCity", [])
        )
        assert temperature is None
