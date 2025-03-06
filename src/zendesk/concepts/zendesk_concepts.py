"""
This module contains the concepts for Zendesk.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from kognitos.bdk.decorators import concept


@concept(is_a="zendesk ticket")
@dataclass
class ZendeskTicket:
    """
    A ticket in Zendesk.

    Attributes:
        ticket_id: The ID of the ticket.
        comment: The comment of the ticket.
        metadata: The metadata of the ticket.
        requester: The requester of the ticket.
        satisfaction_rating: The satisfaction rating of the ticket.
        via: The via of the ticket.
        voice_comment: The voice comment of the ticket.
        allow_attachments: Whether the ticket allows attachments.
        allow_channelback: Whether the ticket allows channelback.
        from_messaging_channel: Whether the ticket is from a messaging channel.
        is_public: Whether the ticket is public.
        macro_id: The ID of the macro.
        safe_update: Whether the ticket is safe to update.
        assignee_email: The email of the assignee.
        description: The description of the ticket.
        due_at: The due date of the ticket.
        external_id: The external ID of the ticket.
        priority: The priority of the ticket.
        raw_subject: The raw subject of the ticket.
        recipient: The recipient of the ticket.
        status: The status of the ticket.
        subject: The subject of the ticket.
        type: The type of the ticket.
        problem_id: The ID of the problem.
        assignee_id: The ID of the assignee.
        brand_id: The ID of the brand.
        group_id: The ID of the group.
        organization_id: The ID of the organization.
        requester_id: The ID of the requester.
        submitter_id: The ID of the submitter.
        ticket_form_id: The ID of the ticket form.
        via_followup_source_id: The ID of the via followup source.
        via_id: The ID of the via.
        attribute_value_ids: The IDs of the attribute values.
        collaborator_ids: The IDs of the collaborators.
        collaborators: The collaborators of the ticket.
        custom_fields: The custom fields of the ticket.
        email_cc_ids: The IDs of the email CCs.
        email_ccs: The email CCs of the ticket.
        follower_ids: The IDs of the followers.
        followers: The followers of the ticket.
        followup_ids: The IDs of the followups.
        macro_ids: The IDs of the macros.
        sharing_agreement_ids: The IDs of the sharing agreements.
        tags: The tags of the ticket.
    """

    ticket_id: str
    comment: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    requester: Optional[Dict[str, Any]] = None
    satisfaction_rating: Optional[Dict[str, Any]] = None
    via: Optional[Dict[str, Any]] = None
    voice_comment: Optional[Dict[str, Any]] = None
    allow_attachments: Optional[bool] = None
    allow_channelback: Optional[bool] = None
    from_messaging_channel: Optional[bool] = None
    is_public: Optional[bool] = None
    macro_id: Optional[int] = None
    safe_update: Optional[bool] = None
    assignee_email: Optional[str] = None
    description: Optional[str] = None
    due_at: Optional[str] = None
    external_id: Optional[str] = None
    priority: Optional[str] = None
    raw_subject: Optional[str] = None
    recipient: Optional[str] = None
    status: Optional[str] = None
    subject: Optional[str] = None
    type: Optional[str] = None
    problem_id: Optional[int] = None
    assignee_id: Optional[int] = None
    brand_id: Optional[int] = None
    group_id: Optional[int] = None
    organization_id: Optional[int] = None
    requester_id: Optional[int] = None
    submitter_id: Optional[int] = None
    ticket_form_id: Optional[int] = None
    via_followup_source_id: Optional[int] = None
    via_id: Optional[int] = None
    attribute_value_ids: Optional[List[int]] = None
    collaborator_ids: Optional[List[int]] = None
    collaborators: Optional[List[Dict[str, Any]]] = None
    custom_fields: Optional[List[Dict[str, Any]]] = None
    email_cc_ids: Optional[List[int]] = None
    email_ccs: Optional[List[Dict[str, Any]]] = None
    follower_ids: Optional[List[int]] = None
    followers: Optional[List[Dict[str, Any]]] = None
    followup_ids: Optional[List[int]] = None
    macro_ids: Optional[List[int]] = None
    sharing_agreement_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None

