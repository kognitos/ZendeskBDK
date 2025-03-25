"""
A short description of the project.
"""

import json
import logging
import os
import typing
from collections import namedtuple
from dataclasses import fields
from typing import Optional, Union
from urllib.parse import quote, urlencode
import requests
import zenpy  # type: ignore
from dateutil.parser import ParserError, parse
from kognitos.bdk.api import NounPhrase
from kognitos.bdk.decorators import book, config, connect, procedure
from zenpy import Zenpy
from zenpy.lib.api_objects import Comment, Ticket  # type: ignore
from zenpy.lib.exception import RecordNotFoundException  # type: ignore
from zendesk.concepts.zendesk_concepts import ZendeskTicket

DEFAULT_TIMEOUT = 30000

# metadata = {
#     "comment": FieldProperties("comment", dict, []),
#     "metadata": FieldProperties("metadata", dict, []),
#     "requester": FieldProperties("requester", dict, []),
#     "satisfaction_rating": FieldProperties("satisfaction_rating", dict, []),
#     "via": FieldProperties("via", dict, []),
#     "voice_comment": FieldProperties("voice_comment", dict, []),
#     "allow_attachments": FieldProperties("allow_attachments", bool, []),
#     "allow_channelback": FieldProperties("allow_channelback", bool, []),
#     "from_messaging_channel": FieldProperties("from_messaging_channel", bool, []),
#     "is_public": FieldProperties("is_public", bool, []),
#     "macro_id": FieldProperties("macro_id", bool, []),
#     "safe_update": FieldProperties("safe_update", bool, []),
#     "assignee_email": FieldProperties("assignee_email", str, []),
#     "description": FieldProperties("description", str, []),
#     "due_at": FieldProperties("due_at", str, []),
#     "external_id": FieldProperties("external_id", str, []),
#     "priority": FieldProperties("priority", str, ["urgent", "high", "normal", "low"]),
#     "raw_subject": FieldProperties("raw_subject", str, []),
#     "recipient": FieldProperties("recipient", str, []),
#     "status": FieldProperties(
#         "status", str, ["new", "open", "pending", "hold", "solved", "closed"]
#     ),
#     "subject": FieldProperties("subject", str, []),
#     "type": FieldProperties(
#         "subject", str, ["problem", "incident", "question", "task", "unknown"]
#     ),
#     "problem_id": FieldProperties("problem_id", int, []),
#     "assignee_id": FieldProperties("assignee_id", int, []),
#     "brand_id": FieldProperties("brand_id", int, []),
#     "group_id": FieldProperties("group_id", int, []),
#     "organization_id": FieldProperties("organization_id", int, []),
#     "requester_id": FieldProperties("requester_id", int, []),
#     "submitter_id": FieldProperties("submitter_id", int, []),
#     "ticket_form_id": FieldProperties("ticket_form_id", int, []),
#     "via_followup_source_id": FieldProperties("via_followup_source_id", int, []),
#     "via_id": FieldProperties("via_id", int, []),
#     "attribute_value_ids": FieldProperties("attribute_value_ids", list, []),
#     "collaborator_ids": FieldProperties("collaborator_ids", list, []),
#     "collaborators": FieldProperties("collaborators", list, []),
#     "custom_fields": FieldProperties("custom_fields", list, []),
#     "email_cc_ids": FieldProperties("email_cc_ids", list, []),
#     "email_ccs": FieldProperties("email_ccs", list, []),
#     "follower_ids": FieldProperties("follower_ids", list, []),
#     "followers": FieldProperties("followers", list, []),
#     "followup_ids": FieldProperties("followup_ids", list, []),
#     "macro_ids": FieldProperties("macro_ids", list, []),
#     "sharing_agreement_ids": FieldProperties("sharing_agreement_ids", list, []),
#     "tags": FieldProperties("tags", list, []),
# }

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZendeskProxy:
    """
    A proxy class for interacting with Zendesk API.
    """

    def __init__(self, creds_dict: typing.Dict):
        self.subdomain = creds_dict["subdomain"]
        self.email = creds_dict["email"]
        self.token = creds_dict["token"]
        self.password = creds_dict["password"]

    @property
    def client(self):
        """
        Returns a Zenpy client for interacting with Zendesk API.
        """
        return Zenpy(subdomain=self.subdomain, email=self.email, token=self.token)

    def validate_custom(self, val, field_metadata):
        """
        Validates and converts the value of a custom field.
        """
        # Dict fields conversions
        if field_metadata.name == "comment" and not isinstance(val, dict):
            if isinstance(val, str):
                val = {"body": val}
            else:
                raise ValueError(f"Invalid field value for {field_metadata.name}")

        elif field_metadata.name == "requester" and not isinstance(val, dict):
            if isinstance(val, str):
                val = {"email": val}  # Expect email by default
            else:
                raise ValueError(f"Invalid field value for {field_metadata.name}")

        elif field_metadata.name == "satisfaction_rating" and not isinstance(val, dict):
            if isinstance(val, str):
                if val in ["good," "bad", "unspecified"]:
                    val = {"score": val}
                else:
                    val = {"comment": val}
            else:
                raise ValueError(f"Invalid field value for {field_metadata.name}")

        # Check fields having specific options to choose from
        elif field_metadata.options and val not in field_metadata.options:
            raise ValueError(f"Invalid field value for {field_metadata.name}")

        return val

    def validate_and_convert_value(self, val, field_metadata):
        """
        Validates and converts the value of a field.
        """
        val = self.validate_custom(val, field_metadata)

        if field_metadata.type == str:
            val = str(val)
        elif field_metadata.type == int:
            val = int(val)
        elif field_metadata.type == bool and val not in [
            "true",
            "false",
            True,
            False,
            0,
            1,
        ]:
            val = False
        elif not isinstance(val, field_metadata.type):
            raise RuntimeError(
                f"the input value should be python '{field_metadata.type}', got {type(val).__name__}"
            )
        return val

    def is_update_ticket_data_valid(self, data):
        """
        Validates the data for updating a ticket.
        """
        if not data:
            return
        if data.get("due_at"):
            if not parse(data.get("due_at")):
                raise ParserError()
            if data.get("type") and data.get("type") != "task":
                raise ValueError("ticket must be of type `task` to assign due date")

        return

    def is_query_fields_valid(self, query):
        """
        Validates the fields for a query.
        """
        field_list = []
        query_fields = fields(ZendeskTicket)
        for sub_query in query.split(" "):
            if ":" in sub_query:
                field_list.append(sub_query.split(":")[0])

        for field in field_list:
            if field not in query_fields:
                return False, ValueError(f"Query field {field} is not valid choice")
        return True, None


def get_zendesk_connection(connection_data: dict) -> ZendeskProxy:
    """
    Returns a ZendeskProxy object for interacting with Zendesk API.
    """
    if connection_data is None:
        raise ValueError(
            'Connection Data is empty.  Maybe you forgot to connect to Zendesk.  Try "connect to zendesk" first'
        )
    try:
        if isinstance(connection_data, str):
            connection_data_dict = json.loads(connection_data)
        else:
            connection_data_dict = connection_data
        if not isinstance(connection_data_dict, dict):
            raise ValueError("need connection data to connect to Zendesk")
        return ZendeskProxy(creds_dict=connection_data_dict)
    except TypeError as e:
        raise EnvironmentError(
            "connection data is invalid.  Maybe you forgot to connect to Zendesk"
        ) from e
    except Exception as e:
        raise ValueError("cannot connect to Zendesk") from e


def ticket_to_dict(ticket: Ticket) -> dict:
    """
    Convert a Zenpy Ticket object to a dictionary.
    """
    if not ticket:
        return {}

    return {
        "id": ticket.id,
        "url": ticket.url,
        "subject": ticket.subject,
        "description": ticket.description,
        "status": ticket.status,
        "priority": ticket.priority,
        "type": ticket.type,
        "tags": ticket.tags,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at,
        "due_at": ticket.due_at,
        "assignee": {
            "name": "" if not ticket.assignee else ticket.assignee.name,
            "email": "" if not ticket.assignee else ticket.assignee.email,
            "id": "" if not ticket.assignee else ticket.assignee.id,
        },
        "requester": {
            "name": "" if not ticket.requester else ticket.requester.name,
            "email": "" if not ticket.requester else ticket.requester.email,
            "id": "" if not ticket.requester else ticket.requester.id,
        },
        "organization": {
            "name": "" if not ticket.organization else ticket.organization.name,
            "id": "" if not ticket.organization else ticket.organization.id,
        },
    }


# Main functions
def search_without_pagination_using_client(
    zendesk_proxy: ZendeskProxy, entity_type: str
):
    """
    Search for entities without pagination using the Zendesk client.
    Zendesk also supports custom fields

    see https://support.zendesk.com/hc/en-us/articles/4408886879258
    only offset pagination is upported which may result in duplicate results
    https://developer.zendesk.com/api-reference/ticketing/ticket-management/search/#available-parameters
    see search_with_pagination_using_requests()
    """
    objs = []
    for ticket in zendesk_proxy.client.search("zenpy", type=entity_type):
        objs.append(ticket)
    return objs


def search_with_pagination_using_requests(
    zendesk_proxy: ZendeskProxy, query, cursor=None, entity_type="ticket", page_size=100
):
    """
    Search for entities with pagination using the Zendesk API.
    """
    # Validate query fields
    _, err = zendesk_proxy.is_query_fields_valid(query)
    if err:
        raise err

    # The parameters for the API call
    params = {
        "query": query,
        "page[size]": page_size,
        "filter[type]": entity_type,
        "after": cursor,
    }

    # The API endpoint for searching entities
    url = (
        f"https://{zendesk_proxy.SUBDOMAIN}.zendesk.com/api/v2/search/export.json?"
        + urlencode(params)
    )

    # Set the authentication credentials and headers
    auth = (zendesk_proxy.EMAIL, zendesk_proxy.PASSWORD)
    headers = {"Content-Type": "application/json"}

    # Make the API call
    response = requests.get(
        url, auth=auth, headers=headers, params=params, timeout=DEFAULT_TIMEOUT
    )
    response.raise_for_status()
    return response.json(), response.json().get("meta").get("after_cursor")


def create_ticket(zendesk_client: zenpy.Zenpy, ticket_info: dict, attachment=None):
    """
    Create a ticket in Zendesk.
    :param zendesk_client: a Zenpy object to interact with zendesk
    :param ticket_info: a dictionary with ticket data
    :param attachment: a file object need to attach in comment
    :return: ticket object
    """
    ticket = Ticket(**ticket_info)
    if attachment:
        comment = ticket_info.get("comment", "")
        res = zendesk_client.attachments.upload(
            fp=attachment, target_name=attachment.name
        )
        ticket.comment = Comment(
            body=comment.get("body", str(comment)), uploads=[res.token]
        )

    ticket = zendesk_client.tickets.create(ticket).ticket

    return ticket_to_dict(ticket)


def assign_ticket(zendesk_client: zenpy.Zenpy, ticket_id: str, user):
    """
    Assign a ticket to a user in Zendesk.
    """
    # Get the ticket and assign user
    ticket = zendesk_client.tickets(id=ticket_id)

    if user.role and user.role != "agent":
        raise RuntimeError(f"can't assign ticket, user_id:{user.id} is not a agent.")

    # Assign the ticket to the user
    ticket.assignee = user
    ticket = zendesk_client.tickets.update(ticket).ticket

    # Return a success message
    return ticket_to_dict(ticket)


def update_ticket(zendesk_client: zenpy.Zenpy, ticket_id: str, data: dict):
    """
    Update a ticket in Zendesk.
    """
    # Validate incoming data
    # _, err = is_update_ticket_data_valid(data)
    # if err:
    #     raise err

    ticket = zendesk_client.tickets(id=ticket_id)
    if not ticket:
        raise RecordNotFoundException(f"ticket not found for id:{ticket_id}")

    # Allow partial update
    ticket.status = data.get("status") if data.get("status") else ticket.status
    ticket.priority = data.get("priority") if data.get("priority") else ticket.priority
    ticket.due_at = parse(data.get("due_at")) if data.get("due_at") else ticket.due_at
    ticket.type = data.get("type") if data.get("type") else ticket.type

    ticket = zendesk_client.tickets.update(ticket).ticket

    # Return a success message
    return ticket_to_dict(ticket)


def delete_ticket(zendesk_client: zenpy.Zenpy, ticket_id: str):
    """
    Delete a ticket in Zendesk.
    """
    ticket = zendesk_client.tickets(id=ticket_id)
    if not ticket:
        raise RecordNotFoundException(f"ticket with id:{ticket_id} not found")

    zendesk_client.tickets.delete(ticket)

    return "Ticket deleted successfully"


def attach_file(zendesk_client: zenpy.Zenpy, ticket_id: str, file, comment=""):
    """
    Attach a file to a ticket in Zendesk.
    """
    if not file:
        raise ValueError("File object is None")

    ticket = zendesk_client.tickets(id=ticket_id)
    if not ticket:
        raise RecordNotFoundException(f"ticket with id:{ticket_id} not found")

    res = zendesk_client.attachments.upload(fp=file, target_name=file.name)

    ticket.comment = Comment(body=comment, uploads=[res.token])
    zendesk_client.tickets.update(ticket)

    return {"message": "File attached successfully"}


def get_ticket(zendesk_client: zenpy.Zenpy, ticket_id: str):
    """
    Get a ticket in Zendesk.
    """
    ticket = zendesk_client.tickets(id=ticket_id)
    if not ticket:
        raise RecordNotFoundException(f"ticket with id:{ticket_id} not found")
    return ticket_to_dict(ticket)


def search_user(zendesk_client: zenpy.Zenpy, search_value: str, search_type: str):
    """
    Search for a user in Zendesk.
    """
    if search_type == "id":
        user = zendesk_client.users(id=search_value)

    elif search_type in ["name", "email"]:
        search_value = f"type:user {search_value}"
        users = zendesk_client.search(query=search_value)
        if users.count > 0:
            user = users[0:1][0]
        else:
            user = None
    else:
        raise RuntimeError("Invalid search type. Please specify 'id', or 'name'.")
    return user


@book(name="Zendesk", icon="data/icon.svg")
class ZendeskBook:
    """
    Zendesk book enables users to create, update, delete, and get tickets in Zendesk.

    Author:
        Kognitos, Inc.
    """

    def __init__(self):
        """
        Initializes an instance of the class.
        """
        self._timeout = float(DEFAULT_TIMEOUT)
        self._zendesk_proxy = None

    @property
    @config(default_value=DEFAULT_TIMEOUT)
    def timeout(self) -> float:
        """
        Timeout in seconds when making API calls to Zendesk
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: float):
        """
        Sets the timeout value in seconds.
        """
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self._timeout = timeout

    @connect(noun_phrase="credentials")
    def connect(
        self,
        zendesk_subdomain: str,
        zendesk_email: str,
        zendesk_token: str,
        zendesk_password: str,
    ):
        """
        Connects to Zendesk using the provided credentials. This procedure is necessary for performing operations that require Zendesk access.

        Arguments:
            zendesk_subdomain (string): The subdomain of your Zendesk account.
            zendesk_email (string): The email associated with your Zendesk account.
            zendesk_token (string): The API token from Zendesk. This is preferred for authentication.
            zendesk_password (string): The password for your Zendesk account. This is an alternative to the API token and is not recommended for security reasons.

        Labels:
            zendesk_token: Zendesk Token
            zendesk_subdomain: Zendesk Subdomain
            zendesk_email: Zendesk Email
            zendesk_password: Zendesk Password

        Examples of usage in KOG language:
        ```
        connect to zendesk via credentials<----
            the zendesk subdomain is "mycompany"
            the zendesk email is "support@mycompany.com"
            the zendesk token is "<api_token>"
            the zendesk password is "<password>"
        ```
        """
        creds_dict = {}
        creds_dict["subdomain"] = zendesk_subdomain
        creds_dict["email"] = zendesk_email
        creds_dict["token"] = zendesk_token
        creds_dict["password"] = zendesk_password

        self._zendesk_proxy = ZendeskProxy(creds_dict)

    @procedure("to create a ticket in zendesk")
    def to_create_a_ticket_in_zendesk(self, ticket: ZendeskTicket):
        """
        Creates a new ticket or object in Zendesk with the specified details.

        Input Concepts
            thing (string): The type of object to be created in Zendesk. This is typically a ticket.

        Returns:
            A zendesk object representing the created ticket or object.

        Examples of usage in KOG language:
            ```
            create a json
            the json is a zendesk ticket
            the zendesk ticket's comment is "This is a test ticket"
            the zendesk ticket's subject is "Test"

            ```
        """
        # payload = {}
        # required_field_list = ["comment"]
        # zendesk_client = get_zendesk_connection(self._zendesk_proxy)

        payload = {}
        if not ticket.comment:
            raise ValueError("Comment is required")
        ticket.comment = {"body": ticket.comment}
        for field in fields(ticket):
            payload[field.name] = getattr(ticket, field.name)

        record = create_ticket(self._zendesk_proxy.client, payload)
        return record
        # return ConceptCreateParams(value=record, is_a="zendesk_object")

    @procedure("to assign a (ticket) in zendesk")
    def to_assign_a_ticket_in_zendesk(self, ticket_id: str, assignee: str):
        """
            Assigns a ticket to a user in Zendesk based on the provided assignee identifier.

        Input Concepts:
            ticket_id (string): The ID of the ticket to be assigned.
            assignee (string): The identifier of the user to whom the ticket will be assigned. This can be a user ID, email, or name.

        Returns:
            The result of the ticket assignment operation.

        Examples of usage in KOG language:
            ```
            assign the ticket in zendesk with # <----
                the ticket_id is "12345"
                the assignee is "john.doe@example.com"
            ```
            ```
            assign the ticket in zendesk with # <----
                the ticket_id is "67890"
                the assignee is "98765" # Assuming this is a user ID
            ```
        """

        if assignee.isnumeric():
            search_type = "id"
        elif "@" in assignee:
            search_type = "email"
        else:
            search_type = "name"

        user = search_user(
            self._zendesk_proxy.client, search_value=assignee, search_type=search_type
        )
        if not user:
            raise ValueError(f"No user found with given {search_type}: {assignee}")
        result = assign_ticket(
            self._zendesk_proxy.client, ticket_id=ticket_id, user=user
        )
        return result

    @procedure("to update a ticket in zendesk")
    def to_update_a_ticket_in_zendesk(self, ticket: ZendeskTicket):
        """
            Updates a specific ticket in Zendesk with the provided information.

        Input Concepts:
            ticket_id (string): The ID of the ticket to be updated in Zendesk.

        Returns:
            The updated ticket information as returned by Zendesk.

        Examples of usage in KOG language:
            ```
            update the ticket in zendesk with # <----
                the ticket_id is "12345"
                the status is "open"
                the priority is "high"
            ```

            ```
            update the ticket in zendesk with # <----
                the ticket_id is "67890"
                the assignee is "agent_id"
                the comment is "Updated details as requested."
            ```
        """

        # check if user id is valid
        update_payload = {}
        if not ticket.ticket_id:
            raise ValueError("Ticket ID is required")

        for field in fields(ticket):
            update_payload[field.name] = getattr(ticket, field.name)

        # paths = [{"path": ["the", path]} for path in metadata.keys()]
        # optional_fields = brain.resolve_all(
        #     paths=paths, message="Please provide", request=False
        # )

        # update_payload = {}
        # for field in optional_fields:
        #     if not field.value:
        #         continue
        #     field_metadata = metadata.get(field.path[1])
        #     update_payload[field.path[1]] = zendesk_client.validate_and_convert_value(
        #         field.value, field_metadata
        #     )

        self._zendesk_proxy.is_update_ticket_data_valid(update_payload)

        record = update_ticket(
            self._zendesk_proxy.client, ticket_id=ticket.ticket_id, data=update_payload
        )
        return record

    @procedure("to delete a (ticket) in zendesk")
    def to_delete_a_ticket_in_zendesk(self, ticket_id: str):
        """
        Deletes a specified ticket in Zendesk.

        Input Concepts:
            the ticket id (number): The ID of the ticket to be deleted in Zendesk.

        Returns:
            the ticket (string): The ID of the ticket that was deleted.

        Examples of usage in KOG language:
            ```
            delete a ticket in zendesk with # <----
                the ticket_id is "67890"
            ```

        """

        record = delete_ticket(self._zendesk_proxy.client, ticket_id=ticket_id)
        return record
    
    @procedure("to get a (ticket) in zendesk")
    def to_get_a_ticket_in_zendesk(self, ticket_id: str):
        """
            Retrieves a specific record from Zendesk based on the provided ticket ID.

        Input Concepts:
            ticket_id (string): The ID of the ticket to retrieve from Zendesk.

        Returns:
            A zendesk object representing the retrieved ticket.

        Examples of usage in KOG language:
            ```
            get a ticket in zendesk with # <----
                the ticket_id is "12345"
            ```
        """

        record = get_ticket(self._zendesk_proxy.client, ticket_id=ticket_id)
        return record
