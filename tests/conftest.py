# pylint: disable=missing-module-docstring, missing-function-docstring
import json
import re

import boto3
import pytest


def scrub_string(pattern, replacement=""):
    def before_record_response(response):
        body = response["body"]["string"].decode("utf-8")
        body = re.sub(pattern, replacement, body)
        response["body"]["string"] = bytes(body, encoding="utf-8")
        return response

    return before_record_response


@pytest.fixture(scope="package")
def vcr_config():
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
    secret_name = "bdk/test/openweather"
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
