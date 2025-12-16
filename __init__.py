"""
stem_racing_app
=================

This package contains a simple prototype of the STEM Racing (F1 in Schools) project‑
management application.  It models the core concepts—roles, deliverables, tasks,
risks and budgets—and provides basic scheduling and reporting features.  While
not a full web application, it demonstrates how the system could be structured
in code.  A command‑line demonstration is provided in ``app.py``.

Modules:

* ``models`` – dataclasses representing roles, tasks, deliverables, risks and budget items.
* ``project`` – a ``Project`` class that aggregates the models and provides methods
  to add roles, tasks and deliverables, and to generate reports.
* ``scheduler`` – functions to create Gantt charts using matplotlib.
* ``risk`` – dataclass and helper functions for risk management.
* ``chat`` – a simple in‑memory chat system supporting channels and messages.
* ``report`` – functions to produce textual status reports.
"""

from models import Role, Deliverable, Task, BudgetItem
from project import Project
from risk import Risk
from chat import ChatSystem
from report import generate_status_report
from scheduler import plot_gantt

__all__ = [
    "Role",
    "Deliverable",
    "Task",
    "BudgetItem",
    "Risk",
    "Project",
    "ChatSystem",
    "generate_status_report",
    "plot_gantt",
]