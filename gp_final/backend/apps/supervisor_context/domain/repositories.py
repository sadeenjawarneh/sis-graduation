"""
Repository Interfaces (Ports) — abstract contracts the infrastructure must fulfill.
The domain knows nothing about Django ORM or any database technology.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import datetime

from .entities import (
    TeamEntity, AvailabilitySlotEntity, MeetingEntity,
    GradingReportEntity, SupervisorRequestEntity,
    TeamFileEntity, NotificationEntity,
)
from .value_objects import MeetingType, SlotMode, RequestStatus, GradingPhase, WeightedGrade


class ITeamRepository(ABC):

    @abstractmethod
    def get_by_id(self, team_id: int) -> Optional[TeamEntity]:
        """Return a TeamEntity or None."""

    @abstractmethod
    def get_teams_for_supervisor(self, supervisor_id: int) -> List[TeamEntity]:
        """All teams assigned to this supervisor."""

    @abstractmethod
    def get_exam_dates(self, team_id: int) -> List[datetime.date]:
        """Exam dates for a team (used to block meeting scheduling)."""

    @abstractmethod
    def assign_supervisor(self, team_id: int, supervisor_id: int) -> None:
        """Assign a supervisor to a team and set status to active."""


class IAvailabilitySlotRepository(ABC):

    @abstractmethod
    def get_by_supervisor(self, supervisor_id: int) -> List[AvailabilitySlotEntity]:
        """All availability slots for a supervisor, ordered by date/time."""

    @abstractmethod
    def get_by_id(self, slot_id: int, supervisor_id: int) -> Optional[AvailabilitySlotEntity]:
        """Single slot owned by this supervisor."""

    @abstractmethod
    def create(
        self,
        supervisor_id: int,
        date:          datetime.date,
        start_time:    datetime.time,
        end_time:      datetime.time,
        mode:          SlotMode,
    ) -> AvailabilitySlotEntity:
        """Persist a new availability slot."""

    @abstractmethod
    def delete(self, slot_id: int, supervisor_id: int) -> bool:
        """Remove a slot; returns True if deleted."""


class IMeetingRepository(ABC):

    @abstractmethod
    def get_booked_slots(
        self, supervisor_id: int
    ) -> List[Tuple[datetime.date, datetime.time]]:
        """All (date, time) pairs already booked for this supervisor."""

    @abstractmethod
    def get_by_supervisor(self, supervisor_id: int) -> List[MeetingEntity]:
        """All meetings for a supervisor."""

    @abstractmethod
    def count_by_supervisor_and_team(self, supervisor_id: int, team_id: int) -> int:
        """Meeting count — used by the fairness checker."""

    @abstractmethod
    def create(
        self,
        supervisor_id: int,
        team_id:       int,
        date:          datetime.date,
        time:          datetime.time,
        meeting_type:  MeetingType,
        topic:         str,
    ) -> MeetingEntity:
        """Persist a new meeting (must be inside an atomic block)."""


class IGradingReportRepository(ABC):

    @abstractmethod
    def get_by_supervisor(self, supervisor_id: int) -> List[GradingReportEntity]:
        """All grading reports submitted by this supervisor."""

    @abstractmethod
    def create(self, entity: GradingReportEntity) -> GradingReportEntity:
        """Persist a new grading report."""


class ISupervisorRequestRepository(ABC):

    @abstractmethod
    def get_pending_for_supervisor(
        self, supervisor_id: int
    ) -> List[SupervisorRequestEntity]:
        """Requests currently targeting this supervisor with status=pending."""

    @abstractmethod
    def get_by_id(self, request_id: int) -> Optional[SupervisorRequestEntity]:
        """Single request by PK."""

    @abstractmethod
    def approve(
        self,
        request_id:    int,
        supervisor_id: int,
    ) -> Optional[SupervisorRequestEntity]:
        """Mark as approved, record decided_at."""

    @abstractmethod
    def forward_or_reject(
        self,
        request_id:           int,
        next_supervisor_id:   Optional[int],
        next_index:           int,
    ) -> Optional[SupervisorRequestEntity]:
        """
        If next_supervisor_id is given → forward (status=pending, advance index).
        Otherwise → all preferences exhausted, status=rejected.
        """


class ITeamFileRepository(ABC):

    @abstractmethod
    def get_for_supervisor_teams(self, supervisor_id: int) -> List[TeamFileEntity]:
        """All files belonging to teams assigned to this supervisor."""

    @abstractmethod
    def get_by_id(self, file_id: int) -> Optional[TeamFileEntity]:
        """Single file by PK."""

    @abstractmethod
    def delete(self, file_id: int) -> bool:
        """Remove a file record; returns True if deleted."""


class INotificationRepository(ABC):

    @abstractmethod
    def get_for_user(self, user_id: int) -> List[NotificationEntity]:
        """All notifications for a user, newest first."""

    @abstractmethod
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read; returns True if found."""

    @abstractmethod
    def delete(self, notification_id: int, user_id: int) -> bool:
        """Remove a notification; returns True if deleted."""

    @abstractmethod
    def create(
        self,
        recipient_id: int,
        title:        str,
        message:      str,
        notif_type:   str,
        team_name:    str = '',
    ) -> NotificationEntity:
        """Persist a new notification."""
