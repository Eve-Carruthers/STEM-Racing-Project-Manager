"""
Data models for the STEM Racing project management app prototype.

These dataclasses define the entities used throughout the application,
including roles, tasks, deliverables, budget items and simple enums for
risk categorisation.  They are intentionally straightforward and can be
extended or replaced with more sophisticated models (e.g. database
models) in a full implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class Role:
    """Represents a team member role such as Team Manager or Design Engineer."""

    name: str
    description: str = ""

    def __str__(self) -> str:  # pragma: no cover
        return self.name


@dataclass
class Deliverable:
    """Represents a deliverable that must be produced for the competition."""

    name: str
    description: str
    due_date: date
    assigned_role: Optional[Role] = None
    completed: bool = False

    def mark_complete(self) -> None:
        self.completed = True

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} (due {self.due_date.isoformat()})"


@dataclass
class Task:
    """Represents a task within the project schedule.

    Tasks may be associated with a deliverable and may depend on other tasks.
    """

    id: int
    name: str
    description: str
    start_date: date
    end_date: date
    deliverable: Optional[Deliverable] = None
    assigned_role: Optional[Role] = None
    dependencies: List[int] = field(default_factory=list)
    progress: float = 0.0  # percent complete from 0.0 to 100.0

    def duration(self) -> int:
        """Compute the duration of the task in days."""
        return (self.end_date - self.start_date).days + 1

    def __str__(self) -> str:  # pragma: no cover
        return f"Task {self.id}: {self.name} ({self.start_date}→{self.end_date})"


@dataclass
class BudgetItem:
    """Represents a single budget entry (income or expense)."""

    description: str
    amount: float
    category: str  # e.g. 'materials', 'sponsorship', 'tools', 'labour'
    date_incurred: date

    def __str__(self) -> str:  # pragma: no cover
        sign = "+" if self.amount >= 0 else "-"
        return f"{self.description}: {sign}${abs(self.amount):.2f}"