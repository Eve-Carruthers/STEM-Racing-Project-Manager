"""
Reporting utilities for the STEM Racing project.

The ``generate_status_report`` function compiles information from the
Project object into a human‑readable text report.  The report includes
deliverable status, task progress, risk overview and budget summary.

In a full application this data would be rendered into a dashboard or
exported to PDF/word documents.  Here we simply compose a string for
demonstration purposes.
"""

from __future__ import annotations

from datetime import date
from typing import List

from .project import Project


def generate_status_report(project: Project) -> str:
    """Generate a status report summarising the project's current state."""
    lines: List[str] = []
    lines.append(f"Status Report for {project.name}")
    lines.append("=" * (len(lines[0])))
    lines.append("")
    # Deliverable status
    lines.append("Deliverables:")
    for d in project.deliverables:
        status = "Completed" if d.completed else "In progress"
        assigned = d.assigned_role.name if d.assigned_role else "Unassigned"
        lines.append(f"- {d.name} (due {d.due_date.isoformat()}, {status}, owner: {assigned})")
    lines.append("")
    # Task status
    lines.append("Tasks:")
    for t in project.tasks:
        progress = f"{t.progress:.0f}%"
        status = "Complete" if t.progress >= 100.0 else "In progress"
        lines.append(
            f"- [{t.id}] {t.name} ({t.start_date.isoformat()}→{t.end_date.isoformat()}) "
            f"{progress}, {status}"
        )
    lines.append("")
    # Risks
    lines.append("Risks:")
    for r in project.risks:
        lines.append(
            f"- {r.name}: P={r.probability}, I={r.impact}, score={r.score}, {r.severity()}"
            + (f", owner {r.owner}" if r.owner else "")
        )
    lines.append("")
    # Budget summary
    income = sum(item.amount for item in project.budget_items if item.amount > 0)
    expense = sum(-item.amount for item in project.budget_items if item.amount < 0)
    lines.append("Budget Summary:")
    lines.append(f"- Total income: ${income:.2f}")
    lines.append(f"- Total expenses: ${expense:.2f}")
    lines.append(f"- Balance: ${income - expense:.2f}")
    return "\n".join(lines)