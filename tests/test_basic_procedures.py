"""
This module contains the tests for the basic procedures of Zendesk.
"""

import pytest
import logging
from zenpy.lib.exception import RecordNotFoundException
import os
from dotenv import load_dotenv

from zendesk import ZendeskBook

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


def test_get_ticket_success(connected_zendesk_book):
    """
    Test for getting a ticket in Zendesk.
    """
    # Assuming there's a valid ticket with ID 12345
    ticket_id = "5"
    logging.debug(f"Getting ticket with ID: {ticket_id}")
    result = connected_zendesk_book.to_get_a_ticket_in_zendesk(ticket_id)
    logging.info(result)
    assert result is not None


def test_get_ticket_not_found(connected_zendesk_book):
    """
    Test for getting a ticket in Zendesk that is not found.
    """
    with pytest.raises(RecordNotFoundException) as exc_info:
        logging.debug(f"Getting ticket with ID: 99999")
        connected_zendesk_book.to_get_a_ticket_in_zendesk("99999")
        logging.debug(f"Ticket not found")

    assert "error" in str(exc_info.value)


def test_delete_ticket_success(connected_zendesk_book):
    """
    Test for deleting a ticket in Zendesk.
    """
    # Assuming there's a valid ticket with ID 12345
    ticket_id = "13"
    logging.debug(f"Deleting ticket with ID: {ticket_id}")
    result = connected_zendesk_book.to_delete_a_ticket_in_zendesk(ticket_id)
    logging.debug(f"Ticket deleted successfully")
    assert result is None

def test_delete_ticket_not_found(connected_zendesk_book):
    """
    Test for deleting a ticket in Zendesk that is not found.
    """
    with pytest.raises(RecordNotFoundException) as exc_info:
        logging.debug(f"Deleting ticket with ID: 99999")
        connected_zendesk_book.to_delete_a_ticket_in_zendesk("99999")
        logging.debug(f"Ticket not found")

    assert "error" in str(exc_info.value)


def test_assign_ticket_success(connected_zendesk_book):
    """
    Test for assigning a ticket in Zendesk.
    """
    # Assuming there's a valid ticket and agent
    ticket_id = "6"
    agent_name = "ANGSHU ADHYA"
    logging.debug(f"Assigning ticket with ID: {ticket_id} to agent with name: {agent_name}")
    result = connected_zendesk_book.to_assign_a_ticket_in_zendesk(
        ticket_id, agent_name
    )
    logging.debug(f"Ticket assigned successfully")
    assert result is not None


def test_assign_ticket_invalid_agent(connected_zendesk_book):
    """
    Test for assigning a ticket in Zendesk with an invalid agent.
    """
    ticket_id = "12345"
    invalid_agent = "nonexistent@example.com"
    logging.debug(f"Assigning ticket with ID: {ticket_id} to invalid agent with email: {invalid_agent}")
    with pytest.raises(ValueError) as exc_info:
        connected_zendesk_book.to_assign_a_ticket_in_zendesk(
            ticket_id, invalid_agent
        )
    logging.debug(f"Ticket not found")
    assert f"error" in str(exc_info.value)


def test_assign_ticket_not_found(connected_zendesk_book):
    """
    Test for assigning a ticket in Zendesk that is not found.
    """
    agent_email = "agent@example.com"

    with pytest.raises(RecordNotFoundException) as exc_info:
        connected_zendesk_book.to_assign_a_ticket_in_zendesk("99999", agent_email)

    assert "error" in str(exc_info.value)
