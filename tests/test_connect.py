# pylint: disable=missing-module-docstring, missing-function-docstring
import pytest
from requests import HTTPError
from dotenv import load_dotenv
import os

from zendesk import ZendeskBook

load_dotenv()

@pytest.fixture
def zendesk_book():
    return ZendeskBook()

def test_connect_valid_credentials(zendesk_book, aws_secret):
    zendesk_book.connect(
            os.getenv("ZENDESK_SUBDOMAIN"),
            os.getenv("ZENDESK_EMAIL"),
            os.getenv("ZENDESK_TOKEN"),
            os.getenv("ZENDESK_PASSWORD"),
        )
    assert zendesk_book._zendesk_proxy is not None


def test_connect_invalid_credentials(zendesk_book):
        zendesk_book.connect(
            "invalid-subdomain",
            "invalid@email.com",
            "invalid-token",
            "invalid-password",
        )
        assert zendesk_book._zendesk_proxy.subdomain is "invalid-subdomain"


def test_connect_missing_credentials(zendesk_book):
    zendesk_book.connect(None, None, None, None)
    assert zendesk_book._zendesk_proxy.subdomain is None


def test_connect_empty_credentials(zendesk_book):
    zendesk_book.connect("", "", "", "")
    assert zendesk_book._zendesk_proxy.subdomain is ""
