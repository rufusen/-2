"""
Unit-тести для сервісного шару (модуль services).
Перевіряють бізнес-логіку обліку часу, формування інвойсів та управління проєктами.
"""

import pytest
from datetime import datetime, timedelta

from src.billing import OvertimeBilling, StandardBilling
from src.models import Project, Task, TaskStatus, TimeEntry, User
from src.services import InvoiceService, ProjectService, TimeTrackingService


class TestTimeTrackingService:
    """Тести для сервісу обліку робочого часу."""

    def test_log_manual_entry(self):
        service = TimeTrackingService()
        task = Task(title="Розробка API")
        user = User(name="Іван", hourly_rate=500)
        start = datetime(2026, 1, 10, 9, 0)
        end = datetime(2026, 1, 10, 17, 0)

        entry = service.log_manual_entry(task, user, start, end, "Розробка")
        assert entry.duration_hours() == 8.0
        assert len(task.time_entries) == 1

    def test_log_manual_entry_invalid_times(self):
        service = TimeTrackingService()
        task = Task(title="Тест")
        user = User(name="Оля")
        start = datetime(2026, 1, 10, 17, 0)
        end = datetime(2026, 1, 10, 9, 0)

        with pytest.raises(ValueError, match="Час завершення"):
            service.log_manual_entry(task, user, start, end)

    def test_start_timer_changes_status(self):
        service = TimeTrackingService()
        task = Task(title="Дизайн", status=TaskStatus.TODO)
        user = User(name="Марія")
        entry = service.start_timer(task, user)
        assert task.status == TaskStatus.IN_PROGRESS
        duration = service.stop_timer(entry)
        assert duration >= 0.0


class TestInvoiceService:
    """Тести для сервісу формування інвойсів."""

    def _make_project_with_hours(self, hours: float) -> Project:
        project = Project(name="Тестовий проєкт")
        task = Task(title="Завдання 1")
        start = datetime(2026, 1, 10, 9, 0)
        end = start + timedelta(hours=hours)
        entry = TimeEntry(start_time=start, end_time=end)
        task.log_time(entry)
        project.add_task(task)
        return project

    def test_generate_invoice_standard(self):
        project = self._make_project_with_hours(10)
        service = InvoiceService(StandardBilling())
        invoice = service.generate_invoice(project, rate=100)
        assert invoice.total == 1000.0
        assert len(invoice.items) == 1

    def test_generate_invoice_overtime(self):
        project = self._make_project_with_hours(10)
        service = InvoiceService(OvertimeBilling())
        invoice = service.generate_invoice(project, rate=100)
        # 8*100 + 2*100*1.5 = 1100
        assert invoice.total == 1100.0

    def test_empty_project_invoice(self):
        project = Project(name="Порожній проєкт")
        service = InvoiceService()
        invoice = service.generate_invoice(project, rate=100)
        assert invoice.total == 0.0
        assert len(invoice.items) == 0

    def test_negative_rate_invoice_raises(self):
        project = Project(name="Проєкт")
        service = InvoiceService()
        with pytest.raises(ValueError, match="Ставка"):
            service.generate_invoice(project, rate=-50)


class TestProjectService:
    """Тести для сервісу управління проєктами."""

    def test_create_and_get_project(self):
        service = ProjectService()
        project = service.create_project("Time Tracker", "Опис")
        retrieved = service.get_project(project.project_id)
        assert retrieved is not None
        assert retrieved.name == "Time Tracker"

    def test_list_projects(self):
        service = ProjectService()
        service.create_project("Проєкт 1")
        service.create_project("Проєкт 2")
        assert len(service.list_projects()) == 2

    def test_add_task_to_nonexistent_project(self):
        service = ProjectService()
        with pytest.raises(ValueError, match="не знайдено"):
            service.add_task_to_project("fake-id", Task(title="X"))

    def test_project_summary(self):
        service = ProjectService()
        project = service.create_project("Demo")
        t1 = Task(title="Зроблено", status=TaskStatus.DONE)
        t2 = Task(title="В процесі", status=TaskStatus.IN_PROGRESS)
        service.add_task_to_project(project.project_id, t1)
        service.add_task_to_project(project.project_id, t2)
        summary = service.get_project_summary(project.project_id)
        assert summary["total_tasks"] == 2
        assert summary["done_tasks"] == 1
        assert summary["completion_percent"] == 50.0
