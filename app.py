"""
Demonstration script for the STEM Racing project management prototype.

Running this module will create a sample project with roles, deliverables,
tasks, risks and budget items.  It then outputs a status report and
generates a simple Gantt chart.  Use this as a starting point to build
your own project plan or integrate these components into a larger system.

Note: The chat system is not demonstrated here, but you can instantiate
``stem_racing_app.ChatSystem`` directly and interact with it manually.
"""

from __future__ import annotations

from datetime import date, timedelta

from .models import Role, Deliverable, Task, BudgetItem
from .project import Project
from .risk import Risk
from .report import generate_status_report
from .scheduler import plot_gantt


def build_sample_project() -> Project:
    """Construct a sample project with sample data."""
    proj = Project(name="Hydron Racing")
    # Roles
    tm = Role(name="Team Manager", description="Oversees the entire project")
    dm = Role(name="Design Engineer", description="Produces CAD models")
    mm = Role(name="Manufacturing Engineer", description="Builds the cars")
    rm = Role(name="Resource Manager", description="Manages sponsors and resources")
    gm = Role(name="Graphic Designer", description="Produces graphics")
    proj.add_role(tm)
    proj.add_role(dm)
    proj.add_role(mm)
    proj.add_role(rm)
    proj.add_role(gm)
    # Deliverables
    d1 = Deliverable("Car Prototype", "First iteration of the car", date.today() + timedelta(days=30), assigned_role=mm)
    d2 = Deliverable("Engineering Portfolio", "Detailed engineering report", date.today() + timedelta(days=60), assigned_role=dm)
    d3 = Deliverable("Sponsorship Prospectus", "Document for potential sponsors", date.today() + timedelta(days=15), assigned_role=rm)
    proj.add_deliverable(d1)
    proj.add_deliverable(d2)
    proj.add_deliverable(d3)
    # Tasks
    t1 = Task(1, "Research regulations", "Review competition rules", date.today(), date.today() + timedelta(days=7), deliverable=None, assigned_role=tm)
    t2 = Task(2, "Create CAD model", "Design the car in CAD", date.today() + timedelta(days=8), date.today() + timedelta(days=20), deliverable=d1, assigned_role=dm, dependencies=[1])
    t3 = Task(3, "Manufacture prototype", "CNC milling", date.today() + timedelta(days=21), date.today() + timedelta(days=35), deliverable=d1, assigned_role=mm, dependencies=[2])
    t4 = Task(4, "Write engineering portfolio", "Document design process", date.today() + timedelta(days=30), date.today() + timedelta(days=60), deliverable=d2, assigned_role=dm, dependencies=[3])
    t5 = Task(5, "Draft sponsorship prospectus", "Prepare marketing document", date.today(), date.today() + timedelta(days=15), deliverable=d3, assigned_role=rm)
    for t in [t1, t2, t3, t4, t5]:
        proj.add_task(t)
    # Risk examples
    r1 = Risk("Machinery breakdown", "CNC machine may fail", probability=3, impact=4, owner=mm.name, mitigation="Schedule backup machine time")
    r2 = Risk("Sponsor withdrawal", "Sponsor may pull funding", probability=2, impact=5, owner=rm.name, mitigation="Have multiple sponsors lined up")
    proj.add_risk(r1)
    proj.add_risk(r2)
    # Budget entries
    b1 = BudgetItem("Sponsorship income", 2000.0, "income", date.today())
    b2 = BudgetItem("Material costs", -500.0, "materials", date.today() + timedelta(days=10))
    b3 = BudgetItem("Machine time", -300.0, "equipment", date.today() + timedelta(days=25))
    proj.add_budget_item(b1)
    proj.add_budget_item(b2)
    proj.add_budget_item(b3)
    return proj


def main() -> None:  # pragma: no cover
    project = build_sample_project()
    # Print status report
    report = generate_status_report(project)
    print(report)
    # Plot a Gantt chart
    print("\nGenerating Gantt chart... (close the chart window to continue)")
    plot_gantt(project.tasks, title=f"{project.name} Schedule")


if __name__ == "__main__":  # pragma: no cover
    main()