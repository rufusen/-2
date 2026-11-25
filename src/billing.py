"""
Стратегії розрахунку вартості робіт — шаблон GoF «Strategy» (поведінковий).

OCP: щоб додати нову стратегію, достатньо створити новий клас,
     не змінюючи існуючий код.
DIP: клієнтський код (InvoiceService) залежить від протоколу BillingStrategy,
     а не від конкретної реалізації.

── Код «ДО рефакторингу» (проблемний) ──
Раніше розрахунок вартості був захардкожений всередині InvoiceService:

    def calculate(self, hours, rate, billing_type):
        if billing_type == "standard":
            return hours * rate
        elif billing_type == "overtime":
            if hours <= 8:
                return hours * rate
            else:
                return 8 * rate + (hours - 8) * rate * 1.5
        elif billing_type == "fixed":
            return rate
        else:
            raise ValueError("Unknown billing type")

Проблеми:
  - Порушення OCP: додавання нового типу вимагає зміни if/elif.
  - Порушення SRP: InvoiceService відповідає і за формування інвойсу,
    і за логіку розрахунків.
  - Висока цикломатична складність через розгалуження.

── Код «ПІСЛЯ рефакторингу» (нижче) ──
"""

from __future__ import annotations

from src.models import BillingStrategy


class StandardBilling:
    """Стандартна погодинна оплата: hours × rate."""

    def calculate_cost(self, hours: float, rate: float) -> float:
        if hours < 0 or rate < 0:
            raise ValueError("Години та ставка мають бути невід'ємними")
        return round(hours * rate, 2)


class OvertimeBilling:
    """Оплата з надбавкою за понаднормові: перші 8 год — звичайна ставка,
    понад 8 год — ×1.5."""

    NORMAL_HOURS = 8
    OVERTIME_MULTIPLIER = 1.5

    def calculate_cost(self, hours: float, rate: float) -> float:
        if hours < 0 or rate < 0:
            raise ValueError("Години та ставка мають бути невід'ємними")
        if hours <= self.NORMAL_HOURS:
            return round(hours * rate, 2)
        normal_cost = self.NORMAL_HOURS * rate
        overtime_cost = (hours - self.NORMAL_HOURS) * rate * self.OVERTIME_MULTIPLIER
        return round(normal_cost + overtime_cost, 2)


class FixedPriceBilling:
    """Фіксована вартість (rate = фіксована сума, години ігноруються)."""

    def calculate_cost(self, hours: float, rate: float) -> float:
        if hours < 0 or rate < 0:
            raise ValueError("Години та ставка мають бути невід'ємними")
        return round(rate, 2)


# ─────── Контекст стратегії (для зручності) ───────


class BillingContext:
    """
    Контекст, що використовує BillingStrategy.
    Дозволяє змінювати стратегію в рантаймі (GoF Strategy).
    """

    def __init__(self, strategy: BillingStrategy) -> None:
        self._strategy = strategy

    @property
    def strategy(self) -> BillingStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: BillingStrategy) -> None:
        self._strategy = strategy

    def execute(self, hours: float, rate: float) -> float:
        return self._strategy.calculate_cost(hours, rate)
