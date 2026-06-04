"""
Domain Value Objects — immutable, equality-by-value, self-validating.
"""
from dataclasses import dataclass
from enum import Enum
import datetime


# ── Enumerations ──────────────────────────────────────────────────────────────

class MeetingType(str, Enum):
    DIRECT = 'Direct'
    ONLINE = 'Online'


class SlotMode(str, Enum):
    DIRECT = 'Direct'
    ONLINE = 'Online'
    BOTH   = 'Both'


class TeamStatus(str, Enum):
    ACTIVE    = 'active'
    DISBANDED = 'disbanded'


class RequestStatus(str, Enum):
    PENDING   = 'pending'
    APPROVED  = 'approved'
    REJECTED  = 'rejected'
    FORWARDED = 'forwarded'


class GradingPhase(str, Enum):
    PROPOSAL = 'Proposal'
    MIDTERM  = 'Midterm'
    FINAL    = 'Final'


# ── Value Objects ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class MeetingSlot:
    """Represents a specific date+time for a meeting."""
    date: datetime.date
    time: datetime.time

    def __post_init__(self):
        if not isinstance(self.date, datetime.date):
            raise ValueError("date must be a datetime.date instance.")
        if not isinstance(self.time, datetime.time):
            raise ValueError("time must be a datetime.time instance.")


@dataclass(frozen=True)
class WeightedGrade:
    """
    Encapsulates the three grading scores and computes the weighted final grade.
    Weights: chief_supervisor 50%, examiner_one 25%, examiner_two 25%.
    """
    chief_grade:        float
    examiner_one_grade: float
    examiner_two_grade: float

    def __post_init__(self):
        for name, score in [
            ('chief_grade',        self.chief_grade),
            ('examiner_one_grade', self.examiner_one_grade),
            ('examiner_two_grade', self.examiner_two_grade),
        ]:
            if not (0.0 <= score <= 100.0):
                raise ValueError(f"{name} must be between 0 and 100, got {score}.")

    @property
    def final_grade(self) -> float:
        return round(
            self.chief_grade        * 0.50 +
            self.examiner_one_grade * 0.25 +
            self.examiner_two_grade * 0.25,
            2,
        )
