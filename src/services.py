"""
Сервісний шар бізнес-логіки Time Tracker.

SRP: кожен сервіс відповідає за свою область:
  - TimeTrackingService — облік робочого часу
  - InvoiceService — формування інвойсів
  - ProjectService — управління проєктами та завданнями

DIP: InvoiceService залежить від абстракції BillingStrategy (Protocol),
     а не від конкретної реалізації.
"""

from __future__ import annotations

from datetime import datetime

from src.billing import BillingContext, StandardBilling
from src.models import (
    BillingStrategy,
    Invoice,
    InvoiceItem,
    Project,
    Task,
    TaskStatus,
    TimeEntry,
    User,
)


class TimeTrackingService:
    """Сервіс обліку робочого часу (SRP)."""

    def start_timer(self, task: Task, user: User,
                    description: str = "") -> TimeEntry:
        """Розпочати відлік часу для завдання."""
        entry = TimeEntry(
            user=user,
            start_time=datetime.now(),
            description=description,
        )
        task.log_time(entry)
        if task.status == TaskStatus.TODO:
            task.change_status(TaskStatus.IN_PROGRESS)
        return entry

    def stop_timer(self, entry: TimeEntry) -> float:
        """Зупинити відлік часу та повернути тривалість у годинах."""
        if entry.end_time is None:
            entry.end_time = datetime.now()
        return entry.duration_hours()

    def log_manual_entry(self, task: Task, user: User,
                         start: datetime, end: datetime,
                         description: str = "") -> TimeEntry:
        """Вручну записати робочий час."""
        if end <= start:
            raise ValueError("Час завершення має бути після часу початку")
        entry = TimeEntry(
            user=user,
            start_time=start,
            end_time=end,
            description=description,
        )
        task.log_time(entry)
        return entry


class InvoiceService:
    """
    Сервіс формування інвойсів (SRP).
    Використовує BillingStrategy через DIP.
    """

    def __init__(self, billing_strategy: BillingStrategy | None = None) -> None:
        self._billing = BillingContext(billing_strategy or StandardBilling())

    def set_billing_strategy(self, strategy: BillingStrategy) -> None:
        """Змінити стратегію розрахунку вартості."""
        self._billing.strategy = strategy

    def generate_invoice(self, project: Project,
                         rate: float) -> Invoice:
        """Сформувати інвойс для проєкту на основі залогованого часу."""
        if rate < 0:
            raise ValueError("Ставка має бути невід'ємною")
        invoice = Invoice(project=project)

        for task in project.tasks:
            hours = task.get_logged_hours()
            if hours > 0:
                cost = self._billing.execute(hours, rate)
                item = InvoiceItem(
                    description=f"Завдання: {task.title}",
                    hours=round(hours, 2),
                    rate=rate,
                    amount=cost,
                )
                invoice.add_item(item)

        return invoice


class ProjectService:
    """Сервіс управління проєктами (SRP)."""

    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}

    def create_project(self, name: str, description: str = "") -> Project:
        """Створити новий проєкт."""
        project = Project(name=name, description=description)
        self._projects[project.project_id] = project
        return project

    def get_project(self, project_id: str) -> Project | None:
        """Отримати проєкт за ID."""
        return self._projects.get(project_id)

    def list_projects(self) -> list[Project]:
        """Повернути список усіх проєктів."""
        return list(self._projects.values())

    def add_task_to_project(self, project_id: str, task: Task) -> None:
        """Додати завдання до проєкту."""
        project = self._projects.get(project_id)
        if project is None:
            raise ValueError(f"Проєкт з ID {project_id} не знайдено")
        project.add_task(task)

    def get_project_summary(self, project_id: str) -> dict:
        """Отримати зведену інформацію про проєкт."""
        project = self._projects.get(project_id)
        if project is None:
            raise ValueError(f"Проєкт з ID {project_id} не знайдено")
        total_tasks = len(project.tasks)
        done_tasks = 0
        for task in project.tasks:
            if task.status == TaskStatus.DONE:
                done_tasks += 1
        completion_percent = 0.0
        if total_tasks > 0:
            completion_percent = round(done_tasks / total_tasks * 100, 1)
        total_hours = project.get_total_hours()
        return {
            "name": project.name,
            "total_tasks": total_tasks,
            "done_tasks": done_tasks,
            "completion_percent": completion_percent,
            "total_hours": round(total_hours, 2),
        }
