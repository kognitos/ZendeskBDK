# pylint: disable=missing-module-docstring, missing-function-docstring
import math

import pytest
from kognitos.bdk.api import NounPhrase
from requests import HTTPError

from openweather import OpenWeatherBook


@pytest.fixture
def openweather_book():
    book = OpenWeatherBook()
    return book


@pytest.fixture
def connected_openweather_book(openweather_book, aws_secret):
    openweather_book.connect(aws_secret.get("api_key"))
    return openweather_book


@pytest.mark.vcr
def test_api_key_valid(openweather_book, aws_secret):
    openweather_book.connect(aws_secret.get("api_key"))


@pytest.mark.vcr
def test_api_key_invalid(openweather_book):
    with pytest.raises(ValueError):
        openweather_book.connect("not-valid-api-key")


@pytest.mark.vcr
def test_current_temperature(connected_openweather_book):
    temperature = connected_openweather_book.current_temperature(
        NounPhrase("New York", [])
    )
    assert temperature is not None


def convert_to_celsius(value):
    # Convert Fahrenheit to Celsius
    return (value - 32) * 5 / 9


@pytest.mark.vcr
def test_current_temperature_with_units(connected_openweather_book):
    temperature_celsius = connected_openweather_book.current_temperature(
        NounPhrase("New York"), unit=NounPhrase("metric")
    )
    temperature_fahrenheit = connected_openweather_book.current_temperature(
        NounPhrase("New York"), unit=NounPhrase("imperial")
    )
    assert math.isclose(
        temperature_celsius, convert_to_celsius(temperature_fahrenheit), abs_tol=0.4
    )


@pytest.mark.vcr
def test_get_current_temperature_error_response(connected_openweather_book):
    with pytest.raises(HTTPError) as e:
        connected_openweather_book.current_temperature(
            NounPhrase("NonExistentCity", [])
        )

    assert e.value.response.status_code == 404
    assert e.value.request
