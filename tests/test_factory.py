"""
Unit-тести для фабрики завдань (модуль factory).
Перевіряють створення різних типів завдань через Factory Method.
"""

import pytest

from src.factory import (
    BugTaskFactory,
    FeatureTaskFactory,
    GeneralTaskFactory,
    get_task_factory,
)
from src.models import BugTask, FeatureTask, Task, TaskPriority


class TestGeneralTaskFactory:
    """Тести для фабрики загальних завдань."""

    def test_create_general_task(self):
        factory = GeneralTaskFactory()
        task = factory.create_task("Налаштувати CI")
        assert isinstance(task, Task)
        assert task.title == "Налаштувати CI"
        assert task.priority == TaskPriority.MEDIUM

    def test_create_with_priority(self):
        factory = GeneralTaskFactory()
        task = factory.create_task("Urgent", priority=TaskPriority.CRITICAL)
        assert task.priority == TaskPriority.CRITICAL


class TestBugTaskFactory:
    """Тести для фабрики завдань-багів."""

    def test_create_bug_task(self):
        factory = BugTaskFactory(severity="high",
                                 steps_to_reproduce="1. Відкрити сторінку")
        task = factory.create_task("Помилка входу")
        assert isinstance(task, BugTask)
        assert task.severity == "high"
        assert task.priority == TaskPriority.HIGH

    def test_bug_task_is_subtype_of_task(self):
        """LSP: BugTask може використовуватися замість Task."""
        factory = BugTaskFactory()
        task = factory.create_task("Баг")
        assert isinstance(task, Task)


class TestFeatureTaskFactory:
    """Тести для фабрики завдань-фіч."""

    def test_create_feature_task(self):
        factory = FeatureTaskFactory(story_points=5)
        task = factory.create_task("Додати звіти")
        assert isinstance(task, FeatureTask)
        assert task.story_points == 5


class TestGetTaskFactory:
    """Тести для реєстру фабрик."""

    def test_get_known_factory(self):
        factory = get_task_factory("bug", severity="critical")
        assert isinstance(factory, BugTaskFactory)

    def test_get_unknown_factory_raises(self):
        with pytest.raises(ValueError, match="Невідомий тип завдання"):
            get_task_factory("unknown_type")
