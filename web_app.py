"""
Minimal Flask + Socket.IO web interface for the STEM Racing project manager.

The service exposes REST endpoints for creating projects, roles and related
entities backed by a SQLite database.  User authentication is handled via
Flask-Login with a simple role-based access control decorator.  Realtime
chat is provided through Socket.IO and persists messages to the database.
Reports can be exported to PDF or Word by converting the existing
``generate_status_report`` output.
"""
from __future__ import annotations

from datetime import date, datetime
from functools import wraps
from io import BytesIO
from typing import Callable, List

from flask import Flask, abort, jsonify, request, send_file
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_socketio import SocketIO, emit, join_room
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from models import BudgetItem, Deliverable, Role, Task
from project import Project
from report import generate_status_report
from risk import Risk

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stem_racing.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="viewer")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class ProjectModel(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    roles = db.relationship("ProjectRole", backref="project", cascade="all, delete-orphan")
    deliverables = db.relationship("DeliverableRecord", backref="project", cascade="all, delete-orphan")
    tasks = db.relationship("TaskRecord", backref="project", cascade="all, delete-orphan")
    risks = db.relationship("RiskRecord", backref="project", cascade="all, delete-orphan")
    budget_items = db.relationship("BudgetItemRecord", backref="project", cascade="all, delete-orphan")
    chat_messages = db.relationship("ChatMessage", backref="project", cascade="all, delete-orphan")


class ProjectRole(db.Model):
    __tablename__ = "project_roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))


class DeliverableRecord(db.Model):
    __tablename__ = "deliverables"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    completed = db.Column(db.Boolean, default=False)

    assigned_role_id = db.Column(db.Integer, db.ForeignKey("project_roles.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))

    assigned_role = db.relationship("ProjectRole")


class TaskRecord(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    dependencies = db.Column(db.String, default="")
    progress = db.Column(db.Float, default=0.0)

    deliverable_id = db.Column(db.Integer, db.ForeignKey("deliverables.id"))
    assigned_role_id = db.Column(db.Integer, db.ForeignKey("project_roles.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))

    deliverable = db.relationship("DeliverableRecord")
    assigned_role = db.relationship("ProjectRole")

    @property
    def dependency_ids(self) -> List[int]:
        if not self.dependencies:
            return []
        return [int(x) for x in self.dependencies.split(",") if x.strip()]


class RiskRecord(db.Model):
    __tablename__ = "risks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    probability = db.Column(db.Integer, default=1)
    impact = db.Column(db.Integer, default=1)
    owner = db.Column(db.String(120))
    mitigation = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))


class BudgetItemRecord(db.Model):
    __tablename__ = "budget_items"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(80))
    date_incurred = db.Column(db.Date)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(64), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship(User)


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def handle_unauthorized():
    return jsonify({"error": "authentication_required"}), 401


def role_required(*roles: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator


@app.before_first_request
def setup_database() -> None:
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", role="admin")
        admin.set_password("change-me")
        db.session.add(admin)
        db.session.commit()


@app.route("/auth/register", methods=["POST"])
@login_required
@role_required("admin")
def register_user():
    payload = request.get_json(force=True)
    username = payload.get("username")
    password = payload.get("password")
    role = payload.get("role", "viewer")
    if not username or not password:
        abort(400)
    if User.query.filter_by(username=username).first():
        abort(409)
    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "username": user.username, "role": user.role}), 201


@app.route("/auth/login", methods=["POST"])
def login():
    payload = request.get_json(force=True)
    username = payload.get("username")
    password = payload.get("password")
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        abort(401)
    login_user(user)
    return jsonify({"message": "logged_in", "username": user.username, "role": user.role})


@app.route("/auth/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "logged_out"})


@app.route("/projects", methods=["POST"])
@login_required
@role_required("admin", "manager")
def create_project():
    payload = request.get_json(force=True)
    name = payload.get("name")
    description = payload.get("description")
    if not name:
        abort(400)
    project_model = ProjectModel(name=name, description=description)
    db.session.add(project_model)
    db.session.commit()
    return jsonify({"id": project_model.id, "name": project_model.name}), 201


@app.route("/projects/<int:project_id>")
@login_required
def get_project(project_id: int):
    project_model = ProjectModel.query.get_or_404(project_id)
    return jsonify(serialize_project(project_model))


@app.route("/projects/<int:project_id>/roles", methods=["POST"])
@login_required
@role_required("admin", "manager")
def add_role(project_id: int):
    project_model = ProjectModel.query.get_or_404(project_id)
    payload = request.get_json(force=True)
    role = ProjectRole(
        name=payload.get("name"),
        description=payload.get("description"),
        project=project_model,
    )
    db.session.add(role)
    db.session.commit()
    return jsonify({"id": role.id, "name": role.name}), 201


@app.route("/projects/<int:project_id>/deliverables", methods=["POST"])
@login_required
@role_required("admin", "manager")
def add_deliverable(project_id: int):
    project_model = ProjectModel.query.get_or_404(project_id)
    payload = request.get_json(force=True)
    assigned_role = ProjectRole.query.get(payload.get("assigned_role_id"))
    deliverable = DeliverableRecord(
        name=payload.get("name"),
        description=payload.get("description"),
        due_date=parse_date(payload.get("due_date")),
        assigned_role=assigned_role,
        project=project_model,
    )
    db.session.add(deliverable)
    db.session.commit()
    return jsonify({"id": deliverable.id, "name": deliverable.name}), 201


@app.route("/projects/<int:project_id>/tasks", methods=["POST"])
@login_required
@role_required("admin", "manager")
def add_task(project_id: int):
    project_model = ProjectModel.query.get_or_404(project_id)
    payload = request.get_json(force=True)
    deliverable = DeliverableRecord.query.get(payload.get("deliverable_id"))
    assigned_role = ProjectRole.query.get(payload.get("assigned_role_id"))
    task = TaskRecord(
        name=payload.get("name"),
        description=payload.get("description"),
        start_date=parse_date(payload.get("start_date")),
        end_date=parse_date(payload.get("end_date")),
        dependencies=",".join(str(x) for x in payload.get("dependencies", [])),
        progress=float(payload.get("progress", 0.0)),
        deliverable=deliverable,
        assigned_role=assigned_role,
        project=project_model,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({"id": task.id, "name": task.name}), 201


@app.route("/projects/<int:project_id>/risks", methods=["POST"])
@login_required
@role_required("admin", "manager")
def add_risk(project_id: int):
    project_model = ProjectModel.query.get_or_404(project_id)
    payload = request.get_json(force=True)
    risk = RiskRecord(
        name=payload.get("name"),
        description=payload.get("description"),
        probability=int(payload.get("probability", 1)),
        impact=int(payload.get("impact", 1)),
        owner=payload.get("owner"),
        mitigation=payload.get("mitigation"),
        project=project_model,
    )
    db.session.add(risk)
    db.session.commit()
    return jsonify({"id": risk.id, "name": risk.name, "score": risk.probability * risk.impact}), 201


@app.route("/projects/<int:project_id>/budget", methods=["POST"])
@login_required
@role_required("admin", "manager")
def add_budget_item(project_id: int):
    project_model = ProjectModel.query.get_or_404(project_id)
    payload = request.get_json(force=True)
    item = BudgetItemRecord(
        description=payload.get("description"),
        amount=float(payload.get("amount", 0.0)),
        category=payload.get("category"),
        date_incurred=parse_date(payload.get("date")),
        project=project_model,
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"id": item.id, "description": item.description}), 201


@app.route("/projects/<int:project_id>/chat/<channel>")
@login_required
def get_channel_history(project_id: int, channel: str):
    ProjectModel.query.get_or_404(project_id)
    messages = ChatMessage.query.filter_by(project_id=project_id, channel=channel).order_by(ChatMessage.timestamp).all()
    return jsonify([
        {
            "id": m.id,
            "channel": m.channel,
            "author": m.author.username if m.author else "Unknown",
            "content": m.content,
            "timestamp": m.timestamp.isoformat(),
        }
        for m in messages
    ])


@app.route("/projects/<int:project_id>/report/pdf")
@login_required
def export_pdf(project_id: int):
    domain_project = build_domain_project(project_id)
    report_text = generate_status_report(domain_project)
    pdf_bytes = BytesIO()
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(pdf_bytes)
    for i, line in enumerate(report_text.split("\n")):
        c.drawString(50, 800 - i * 15, line)
    c.save()
    pdf_bytes.seek(0)
    return send_file(pdf_bytes, download_name=f"project_{project_id}_report.pdf", mimetype="application/pdf")


@app.route("/projects/<int:project_id>/report/docx")
@login_required
def export_docx(project_id: int):
    domain_project = build_domain_project(project_id)
    report_text = generate_status_report(domain_project)
    from docx import Document

    document = Document()
    for line in report_text.split("\n"):
        document.add_paragraph(line)
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return send_file(buffer, download_name=f"project_{project_id}_report.docx", mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@socketio.on("join")
def handle_join(data):
    channel = data.get("channel")
    project_id = data.get("project_id")
    if not channel or not project_id:
        return
    join_room(channel)
    emit("system", {"message": f"Joined {channel}"})


@socketio.on("chat")
@login_required
def handle_chat(data):
    channel = data.get("channel")
    project_id = data.get("project_id")
    content = data.get("content")
    if not channel or not project_id or not content:
        return
    message = ChatMessage(channel=channel, project_id=project_id, content=content, author_id=current_user.id)
    db.session.add(message)
    db.session.commit()
    payload = {
        "channel": channel,
        "project_id": project_id,
        "author": current_user.username,
        "content": content,
        "timestamp": message.timestamp.isoformat(),
    }
    emit("chat", payload, room=channel)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.fromisoformat(value).date()


def build_domain_project(project_id: int) -> Project:
    project_model = ProjectModel.query.get_or_404(project_id)
    project = Project(name=project_model.name)

    role_map: dict[int, Role] = {}
    for role_record in project_model.roles:
        role = Role(name=role_record.name, description=role_record.description or "")
        project.add_role(role)
        role_map[role_record.id] = role

    deliverable_map: dict[int, Deliverable] = {}
    for deliverable_record in project_model.deliverables:
        deliverable = Deliverable(
            deliverable_record.name,
            deliverable_record.description or "",
            deliverable_record.due_date or date.today(),
            assigned_role=role_map.get(deliverable_record.assigned_role_id),
        )
        deliverable.completed = deliverable_record.completed
        project.add_deliverable(deliverable)
        deliverable_map[deliverable_record.id] = deliverable

    for task_record in project_model.tasks:
        task = Task(
            task_record.id,
            task_record.name,
            task_record.description or "",
            task_record.start_date or date.today(),
            task_record.end_date or date.today(),
            deliverable=deliverable_map.get(task_record.deliverable_id),
            assigned_role=role_map.get(task_record.assigned_role_id),
            dependencies=task_record.dependency_ids,
            progress=task_record.progress,
        )
        project.add_task(task)

    for risk_record in project_model.risks:
        risk = Risk(
            risk_record.name,
            risk_record.description or "",
            probability=risk_record.probability,
            impact=risk_record.impact,
            owner=risk_record.owner,
            mitigation=risk_record.mitigation,
        )
        project.add_risk(risk)

    for budget_record in project_model.budget_items:
        budget_item = BudgetItem(
            budget_record.description,
            budget_record.amount,
            budget_record.category or "",
            budget_record.date_incurred or date.today(),
        )
        project.add_budget_item(budget_item)

    return project


def serialize_project(project_model: ProjectModel) -> dict:
    return {
        "id": project_model.id,
        "name": project_model.name,
        "description": project_model.description,
        "roles": [
            {"id": role.id, "name": role.name, "description": role.description}
            for role in project_model.roles
        ],
        "deliverables": [
            {
                "id": d.id,
                "name": d.name,
                "description": d.description,
                "due_date": d.due_date.isoformat() if d.due_date else None,
                "completed": d.completed,
                "assigned_role_id": d.assigned_role_id,
            }
            for d in project_model.deliverables
        ],
        "tasks": [
            {
                "id": t.id,
                "name": t.name,
                "start_date": t.start_date.isoformat() if t.start_date else None,
                "end_date": t.end_date.isoformat() if t.end_date else None,
                "progress": t.progress,
                "dependencies": t.dependency_ids,
                "deliverable_id": t.deliverable_id,
                "assigned_role_id": t.assigned_role_id,
            }
            for t in project_model.tasks
        ],
        "risks": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "probability": r.probability,
                "impact": r.impact,
                "owner": r.owner,
                "mitigation": r.mitigation,
            }
            for r in project_model.risks
        ],
        "budget": [
            {
                "id": b.id,
                "description": b.description,
                "amount": b.amount,
                "category": b.category,
                "date": b.date_incurred.isoformat() if b.date_incurred else None,
            }
            for b in project_model.budget_items
        ],
    }


if __name__ == "__main__":  # pragma: no cover
    socketio.run(app, debug=True)
