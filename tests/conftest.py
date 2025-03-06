""" Configuration for pytest. """

import json
import re

import boto3
import pytest
from zendesk.book import ZendeskBook

# @pytest.fixture
# def zendesk_book():
#     """
#     Fixture for Zendesk book.
#     """
#     book = ZendeskBook()
#     return book


# @pytest.fixture
# def connected_zendesk_book(zendesk_book, aws_secret):
#     """
#     Fixture for connected Zendesk book.
#     """
#     zendesk_book.connect(
#         aws_secret.get("subdomain"),
#         aws_secret.get("email"),
#         aws_secret.get("token"),
#         aws_secret.get("password"),
#     )
#     return zendesk_book

def scrub_string(pattern, replacement=""):
    """
    Scrubs a string in a response
    """

    def before_record_response(response):
        body = response["body"]["string"].decode("utf-8")
        body = re.sub(pattern, replacement, body)
        response["body"]["string"] = bytes(body, encoding="utf-8")
        return response

    return before_record_response


@pytest.fixture(scope="package")
def vcr_config():
    """
    Configuration for VCR
    """
    return {
        "before_record_response": scrub_string(
            r'\\"api_key\\":\\"[^\\]+\\"',
            r"\"api_key\":\"API_KEY\"",
        ),
        "filter_query_parameters": [("appid", "API_KEY")],
        "filter_headers": ["authorization"],
    }


@pytest.fixture
def aws_secret():
    """
    Retrieve credentials from AWS Secrets Manager
    """
    secret_name = "bdk/test/zendesk_secrets"
    region_name = "us-west-2"

    # Create a Secrets Manager client
    client = boto3.client("secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:  # pylint: disable=broad-exception-caught
        pytest.fail(f"error retrieving secret: {e}")
        return None

    secret = get_secret_value_response.get("SecretString")
    return json.loads(secret) if secret else None
