# STEM Racing Project Management Prototype

This package provides a **prototype** implementation of an F1 in Schools / STEM Racing project‑management application.  It now includes a lightweight Flask web service so the models can be exercised through authenticated HTTP and WebSocket endpoints backed by SQLite persistence.

## Features

- **Data models** for roles, deliverables, tasks, budget items and risks.
- **Project class** to aggregate and manage these entities.
- **Gantt chart generation** using matplotlib to visualise the schedule.
- **Risk scoring** to categorise risks into low/medium/high.
- **Web API** exposing CRUD endpoints for projects, roles, deliverables, tasks, risks and budgets.
- **User authentication and RBAC** powered by Flask‑Login with admin/manager/viewer roles.
- **WebSocket chat** using Socket.IO with persisted message history.
- **Status report generator** summarising deliverables, tasks, risks and budget with export to PDF/Word.

## Getting Started

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Start the web service:

   ```bash
   python web_app.py
   ```

   A default `admin` user (password `change-me`) and SQLite database (`stem_racing.db`) will be created on first run.

3. Use the API and chat service:

   - Authenticate with `POST /auth/login` and use the returned session for subsequent requests.
   - Create projects and related entities via `/projects`, `/projects/<id>/roles`, `/projects/<id>/deliverables`, etc.
   - Connect to the Socket.IO server for real‑time chat with persisted messages.
   - Export status reports from `/projects/<id>/report/pdf` or `/projects/<id>/report/docx`.

## Limitations

- This is **not a full production system**.  It provides a minimal Flask implementation suitable for demos and local workflows.
- The default admin password should be changed before exposing the service.

## Next Steps

- Integrate these models into a web framework (e.g., Flask, Django) with a database backend.
- Implement user authentication and role‑based access control.
- Replace the in‑memory chat system with a websocket‑based chat service or integrate an open‑source solution (e.g., Mattermost/Zulip).
- Add support for exporting reports to PDF or Word formats.