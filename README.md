# Time Tracker — Система управління проєктами та обліку робочого часу

Програмний модуль для управління проєктами та завданнями, фіксації робочого часу (таймером або вручну), розрахунку вартості робіт за змінними стратегіями білінгу та формування інвойсів.

## Структура проєкту

```text
time-tracker/
├── src/
│   ├── __init__.py
│   ├── models.py          # Доменні сутності (User, Project, Task, BugTask, FeatureTask, TimeEntry, Invoice)
│   ├── billing.py         # Стратегії білінгу (GoF Strategy: Standard, Overtime, FixedPrice)
│   ├── factory.py         # Фабрика завдань (GoF Factory Method: General, Bug, Feature)
│   └── services.py        # Сервісний шар (TimeTrackingService, InvoiceService, ProjectService)
├── tests/
│   ├── __init__.py
│   ├── test_billing.py    # 12 unit-тестів для стратегій білінгу
│   ├── test_factory.py    # 7 unit-тестів для фабрик завдань
│   └── test_services.py   # 11 unit-тестів для сервісів
├── diagrams/              # Архітектурні діаграми (UML, C4, CFG, Gitflow)
├── .github/workflows/
│   └── ci.yml             # GitHub Actions CI (flake8 + pytest + coverage)
├── pyproject.toml
├── requirements.txt
├── sonar-project.properties
└── README.md
```

## Принципи SOLID та патерни GoF

- **SRP**: розділення відповідальності між `TimeTrackingService`, `InvoiceService`, `ProjectService` та моделями.
- **OCP**: розширення новими стратегіями білінгу та типами завдань без зміни існуючого коду.
- **LSP**: `BugTask` і `FeatureTask` взаємозамінно підставляються замість `Task`.
- **DIP**: `InvoiceService` залежить від абстракції `BillingStrategy` (`typing.Protocol`).
- **GoF Strategy** (поведінковий): `StandardBilling`, `OvertimeBilling`, `FixedPriceBilling`, `BillingContext`.
- **GoF Factory Method** (твірний): `TaskFactory`, `GeneralTaskFactory`, `BugTaskFactory`, `FeatureTaskFactory`.

## Запуск та тестування

```bash
# Встановити залежності
pip install -r requirements.txt

# Запустити лінтер
pip install flake8
flake8 src/ tests/ --max-line-length=100

# Запустити 30 модульних тестів з покриттям
pytest --cov=src --cov-report=term-missing -v
```
