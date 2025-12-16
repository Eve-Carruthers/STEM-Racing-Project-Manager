# STEM Racing Project Management Prototype

This package provides a **prototype** implementation of an F1 in Schools / STEM Racing project‑management application.  It is not a full product but demonstrates how core features can be modelled and integrated in Python.

## Features

- **Data models** for roles, deliverables, tasks, budget items and risks.
- **Project class** to aggregate and manage these entities.
- **Gantt chart generation** using matplotlib to visualise the schedule.
- **Risk scoring** to categorise risks into low/medium/high.
- **In‑memory chat system** with channels and messages.
- **Status report generator** summarising deliverables, tasks, risks and budget.

## Getting Started

1. Install dependencies.  This prototype relies on `pandas` and `matplotlib`, which should already be installed in the environment.  If not, install via pip:

   ```bash
   pip install pandas matplotlib
   ```

2. Run the demonstration script:

   ```bash
   python -m stem_racing_app.app
   ```

   This will create a sample project, print a status report and display a Gantt chart for the tasks.

3. Explore the code and extend it to suit your workflow.  For example, you can:

   - Add new roles, deliverables and tasks by creating instances of the dataclasses.
   - Use the `Project` object to manage your project and generate reports.
   - Integrate the `ChatSystem` into your UI to support team communication.

## Limitations

- This is **not a full web or mobile app**.  It provides backend logic only.
- Data is stored in memory; there is no persistence across runs.
- The chat system is a simple list of messages and does not support real‑time updates or user authentication.

## Next Steps

- Integrate these models into a web framework (e.g., Flask, Django) with a database backend.
- Implement user authentication and role‑based access control.
- Replace the in‑memory chat system with a websocket‑based chat service or integrate an open‑source solution (e.g., Mattermost/Zulip).
- Add support for exporting reports to PDF or Word formats.