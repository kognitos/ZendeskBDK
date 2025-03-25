"""
This module contains the tests for the basic procedures of Zendesk.
"""

import pytest
import logging
from zenpy.lib.exception import RecordNotFoundException
import os
from dotenv import load_dotenv

from zendesk import ZendeskBook
from zendesk.concepts.zendesk_concepts import ZendeskTicket
load_dotenv()

logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def connected_zendesk_book():
    zendesk_book = ZendeskBook()
    zendesk_book.connect(
        os.getenv("ZENDESK_SUBDOMAIN"),
        os.getenv("ZENDESK_EMAIL"),
        os.getenv("ZENDESK_TOKEN"),
        os.getenv("ZENDESK_PASSWORD"),
    )
    return zendesk_book

def test_create_ticket(connected_zendesk_book):
    logging.debug("Creating a new ticket")
    ticket = ZendeskTicket(
        ticket_id="11",
        comment="This is a test ticket",
    )
    result = connected_zendesk_book.to_create_a_ticket_in_zendesk(
        ticket,
    )
    logging.debug(f"Ticket created: {result}")
    assert result is not None

def test_update_ticket(connected_zendesk_book):
    logging.debug("Updating a ticket")
    ticket = ZendeskTicket(
        ticket_id="24",
        comment="This is a updated ticket",
    )
    result = connected_zendesk_book.to_update_a_ticket_in_zendesk(
        ticket,
    )
    logging.debug(f"Ticket updated: {result}")
    assert result is not None
