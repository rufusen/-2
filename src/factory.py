"""
Фабрика створення завдань — шаблон GoF «Factory Method» (твірний).

OCP: додавання нового типу завдання не вимагає зміни існуючих фабричних методів.
LSP: усі створені завдання — підкласи Task, і можуть використовуватися взаємозамінно.

── Код «ДО рефакторингу» (проблемний) ──

    def create_task(task_type, title, description, **kwargs):
        if task_type == "bug":
            task = Task()
            task.title = title
            task.description = description
            task.severity = kwargs.get("severity", "medium")
            task.steps_to_reproduce = kwargs.get("steps_to_reproduce", "")
            return task
        elif task_type == "feature":
            task = Task()
            task.title = title
            task.description = description
            task.story_points = kwargs.get("story_points", 0)
            return task
        else:
            task = Task()
            task.title = title
            task.description = description
            return task

Проблеми:
  - Порушення OCP: кожен новий тип — додатковий elif.
  - Порушення SRP: один метод знає про всі типи завдань.
  - Відсутність типізації: severity, steps_to_reproduce — динамічні атрибути.

── Код «ПІСЛЯ рефакторингу» (нижче) ──
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.models import BugTask, FeatureTask, Task, TaskPriority


class TaskFactory(ABC):
    """Абстрактна фабрика для створення завдань (Factory Method)."""

    @abstractmethod
    def create_task(self, title: str, description: str = "",
                    priority: TaskPriority = TaskPriority.MEDIUM) -> Task:
        ...


class GeneralTaskFactory(TaskFactory):
    """Фабрика загальних завдань."""

    def create_task(self, title: str, description: str = "",
                    priority: TaskPriority = TaskPriority.MEDIUM) -> Task:
        return Task(title=title, description=description, priority=priority)


class BugTaskFactory(TaskFactory):
    """Фабрика завдань-багів."""

    def __init__(self, severity: str = "medium",
                 steps_to_reproduce: str = "") -> None:
        self.severity = severity
        self.steps_to_reproduce = steps_to_reproduce

    def create_task(self, title: str, description: str = "",
                    priority: TaskPriority = TaskPriority.HIGH) -> BugTask:
        return BugTask(
            title=title,
            description=description,
            priority=priority,
            severity=self.severity,
            steps_to_reproduce=self.steps_to_reproduce,
        )


class FeatureTaskFactory(TaskFactory):
    """Фабрика завдань-фіч."""

    def __init__(self, story_points: int = 0,
                 acceptance_criteria: str = "") -> None:
        self.story_points = story_points
        self.acceptance_criteria = acceptance_criteria

    def create_task(self, title: str, description: str = "",
                    priority: TaskPriority = TaskPriority.MEDIUM) -> FeatureTask:
        return FeatureTask(
            title=title,
            description=description,
            priority=priority,
            story_points=self.story_points,
            acceptance_criteria=self.acceptance_criteria,
        )


# ──────── Реєстр фабрик (для зручності) ────────

_FACTORIES: dict[str, type[TaskFactory]] = {
    "general": GeneralTaskFactory,
    "bug": BugTaskFactory,
    "feature": FeatureTaskFactory,
}


def get_task_factory(task_type: str, **kwargs) -> TaskFactory:
    """Повертає відповідну фабрику за типом завдання."""
    factory_cls = _FACTORIES.get(task_type)
    if factory_cls is None:
        raise ValueError(f"Невідомий тип завдання: {task_type}")
    return factory_cls(**kwargs)
