"""
Project aggregation class.

The Project class aggregates roles, deliverables, tasks, risks and
budget items.  It provides convenience methods to add new items and
perform simple queries.  This class does not persist data; it is meant
to be held in memory for demonstration or testing.  For a production
application, each of these collections would likely be replaced with
database tables.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .models import Role, Deliverable, Task, BudgetItem
from .risk import Risk


@dataclass
class Project:
    name: str
    roles: List[Role] = field(default_factory=list)
    deliverables: List[Deliverable] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)
    risks: List[Risk] = field(default_factory=list)
    budget_items: List[BudgetItem] = field(default_factory=list)

    def add_role(self, role: Role) -> None:
        self.roles.append(role)

    def find_role(self, name: str) -> Optional[Role]:
        for r in self.roles:
            if r.name == name:
                return r
        return None

    def add_deliverable(self, deliverable: Deliverable) -> None:
        self.deliverables.append(deliverable)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def add_risk(self, risk: Risk) -> None:
        self.risks.append(risk)

    def add_budget_item(self, item: BudgetItem) -> None:
        self.budget_items.append(item)

    def get_incomplete_tasks(self) -> List[Task]:
        return [t for t in self.tasks if t.progress < 100.0]

    def get_overdue_tasks(self, today) -> List[Task]:
        return [t for t in self.get_incomplete_tasks() if t.end_date < today]

    def get_high_risks(self) -> List[Risk]:
        return [r for r in self.risks if r.severity() == "High"]