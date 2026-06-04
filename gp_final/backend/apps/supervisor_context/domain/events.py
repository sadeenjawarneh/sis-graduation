"""
Domain Events — facts that happened inside the domain.
Consumers (use cases, infrastructure) react to these events
to trigger side effects such as sending notifications.
"""
from dataclasses import dataclass, field
from typing import List, Optional
import datetime


def _now() -> datetime.datetime:
    from django.utils import timezone
    return timezone.now()


@dataclass
class MeetingScheduledEvent:
    """Raised when a supervisor successfully books a meeting with a team."""
    supervisor_id:   int
    supervisor_name: str
    team_id:         int
    team_name:       str
    member_ids:      List[int]
    date:            datetime.date
    time:            datetime.time
    meeting_type:    str
    topic:           str
    occurred_at:     datetime.datetime = field(default_factory=_now)


@dataclass
class RequestApprovedEvent:
    """Raised when a supervisor approves a supervision request."""
    supervisor_id:   int
    supervisor_name: str
    team_id:         int
    team_name:       str
    member_ids:      List[int]
    occurred_at:     datetime.datetime = field(default_factory=_now)


@dataclass
class RequestForwardedEvent:
    """Raised when a supervisor rejects and the request is forwarded to the next preference."""
    next_supervisor_id: int
    team_name:          str
    project_idea:       str
    occurred_at:        datetime.datetime = field(default_factory=_now)


@dataclass
class RequestExhaustedEvent:
    """Raised when all preferences are exhausted (full rejection)."""
    leader_id:   int
    team_name:   str
    occurred_at: datetime.datetime = field(default_factory=_now)


@dataclass
class GradeSubmittedEvent:
    """Raised when a grading report is created."""
    supervisor_name: str
    team_id:         int
    team_name:       str
    member_ids:      List[int]
    final_grade:     float
    occurred_at:     datetime.datetime = field(default_factory=_now)
