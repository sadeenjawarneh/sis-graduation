"""
Domain Services — logic that belongs to the domain but doesn't fit a single entity.
"""
import datetime
from typing import Optional, Tuple, Dict, List

from .entities import AvailabilitySlotEntity
from .value_objects import MeetingType, SlotMode
from .repositories import IAvailabilitySlotRepository, IMeetingRepository, ITeamRepository


class SlotFinderService:
    """
    Finds the earliest available 30-minute sub-slot for a supervisor
    that matches the requested meeting mode and has no existing booking conflict.
    """

    def __init__(
        self,
        slot_repo:    IAvailabilitySlotRepository,
        meeting_repo: IMeetingRepository,
    ):
        self._slot_repo    = slot_repo
        self._meeting_repo = meeting_repo

    # ── helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _to_minutes(t: datetime.time) -> int:
        return t.hour * 60 + t.minute

    @staticmethod
    def _from_minutes(mins: int) -> datetime.time:
        return datetime.time(hour=mins // 60, minute=mins % 60)

    def _half_hour_sub_slots(
        self, slot: AvailabilitySlotEntity
    ) -> List[datetime.time]:
        start = self._to_minutes(slot.start_time)
        end   = self._to_minutes(slot.end_time)
        result = []
        t = start
        while t + 30 <= end:
            result.append(self._from_minutes(t))
            t += 30
        return result

    # ── public API ───────────────────────────────────────────────────────────

    def find_best_slot(
        self,
        supervisor_id: int,
        meeting_type:  MeetingType,
        exam_dates:    set = None,
    ) -> Optional[Tuple[datetime.date, datetime.time]]:
        """
        Returns (date, time) of the earliest open 30-min sub-slot,
        skipping past slots, already-booked slots, and exam days.
        Returns None if nothing is available.
        """
        from django.utils import timezone

        exam_dates = exam_dates or set()
        all_slots  = self._slot_repo.get_by_supervisor(supervisor_id)
        booked     = set(self._meeting_repo.get_booked_slots(supervisor_id))

        valid_modes = {meeting_type.value, SlotMode.BOTH.value}
        compatible  = [s for s in all_slots if s.mode.value in valid_modes]
        compatible.sort(key=lambda s: (s.date, s.start_time))

        now = timezone.now()
        for slot in compatible:
            if slot.date in exam_dates:
                continue                           # skip exam day entirely
            slot_end_dt = timezone.make_aware(
                datetime.datetime.combine(slot.date, slot.end_time)
            )
            if slot_end_dt < now:
                continue                           # slot is in the past
            for t in self._half_hour_sub_slots(slot):
                if (slot.date, t) not in booked:
                    return slot.date, t

        return None


class FairnessCheckerService:
    """
    Ensures fair meeting distribution across a supervisor's teams.
    A team must not have more than (min_count + 1) meetings compared
    to the supervisor's least-met team.
    """

    def __init__(
        self,
        team_repo:    ITeamRepository,
        meeting_repo: IMeetingRepository,
    ):
        self._team_repo    = team_repo
        self._meeting_repo = meeting_repo

    def check(
        self, supervisor_id: int, team_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Returns (ok, error_message_or_None)."""
        teams = self._team_repo.get_teams_for_supervisor(supervisor_id)
        if len(teams) <= 1:
            return True, None

        counts: Dict[int, int] = {
            t.id: self._meeting_repo.count_by_supervisor_and_team(supervisor_id, t.id)
            for t in teams
        }
        team_count = counts.get(team_id, 0)
        min_count  = min(counts.values())

        if team_count > min_count + 1:
            return False, 'Fair distribution: schedule a team with fewer meetings first.'
        return True, None
