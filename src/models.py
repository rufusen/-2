"""
Доменні моделі системи Time Tracker.

Принципи SOLID, що застосовані:
- SRP: кожен клас відповідає лише за одну сутність/відповідальність.
- OCP: класи відкриті для розширення (нові типи завдань, стратегії),
        закриті для модифікації.
- LSP: підкласи Task можуть використовуватися замість базового класу.
- DIP: модулі залежать від абстракцій (Protocol), а не від конкретних реалізацій.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Protocol


# ──────────────────────────── Enums ────────────────────────────


class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


# ──────────────── Абстракція для DIP (Protocol) ────────────────


class BillingStrategy(Protocol):
    """Стратегія розрахунку вартості робіт (DIP — залежність від абстракції)."""

    def calculate_cost(self, hours: float, rate: float) -> float:
        ...


# ──────────────────────── Доменні моделі ──────────────────────


@dataclass
class User:
    """Користувач системи (SRP — лише дані користувача)."""
    user_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    hourly_rate: float = 0.0
    role: str = "developer"


@dataclass
class Project:
    """Проєкт (SRP — лише дані проєкту)."""
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def get_total_hours(self) -> float:
        return sum(t.get_logged_hours() for t in self.tasks)


@dataclass
class Task:
    """
    Завдання в проєкті (SRP).
    LSP — підкласи BugTask / FeatureTask можуть використовуватися замість Task.
    """
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: User | None = None
    time_entries: list[TimeEntry] = field(default_factory=list)

    def log_time(self, entry: TimeEntry) -> None:
        self.time_entries.append(entry)

    def get_logged_hours(self) -> float:
        total = timedelta()
        for entry in self.time_entries:
            if entry.end_time:
                total += entry.end_time - entry.start_time
        return total.total_seconds() / 3600

    def change_status(self, new_status: TaskStatus) -> None:
        self.status = new_status


# ───── Підкласи Task для демонстрації LSP ─────


@dataclass
class BugTask(Task):
    """Завдання-баг із додатковою інформацією (LSP)."""
    severity: str = "medium"
    steps_to_reproduce: str = ""


@dataclass
class FeatureTask(Task):
    """Завдання-фіча із оцінкою складності (LSP)."""
    story_points: int = 0
    acceptance_criteria: str = ""


@dataclass
class TimeEntry:
    """Запис обліку часу (SRP)."""
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user: User | None = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    description: str = ""

    def duration_hours(self) -> float:
        if self.end_time is None:
            return 0.0
        delta = self.end_time - self.start_time
        return delta.total_seconds() / 3600


@dataclass
class InvoiceItem:
    """Рядок інвойсу (SRP)."""
    description: str = ""
    hours: float = 0.0
    rate: float = 0.0
    amount: float = 0.0


@dataclass
class Invoice:
    """Інвойс / рахунок (SRP)."""
    invoice_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project: Project | None = None
    items: list[InvoiceItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    total: float = 0.0

    def add_item(self, item: InvoiceItem) -> None:
        self.items.append(item)
        self.total = round(self.total + item.amount, 2)
