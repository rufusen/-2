"""
Unit-тести для стратегій білінгу (модуль billing).
Перевіряють коректність розрахунків та граничні випадки.
"""

import pytest

from src.billing import (
    BillingContext,
    FixedPriceBilling,
    OvertimeBilling,
    StandardBilling,
)


class TestStandardBilling:
    """Тести для стандартної погодинної оплати."""

    def test_basic_calculation(self):
        billing = StandardBilling()
        assert billing.calculate_cost(10, 50) == 500.0

    def test_zero_hours(self):
        billing = StandardBilling()
        assert billing.calculate_cost(0, 50) == 0.0

    def test_negative_hours_raises(self):
        billing = StandardBilling()
        with pytest.raises(ValueError):
            billing.calculate_cost(-1, 50)

    def test_fractional_hours(self):
        billing = StandardBilling()
        assert billing.calculate_cost(1.5, 100) == 150.0


class TestOvertimeBilling:
    """Тести для оплати з надбавкою за понаднормові."""

    def test_within_normal_hours(self):
        billing = OvertimeBilling()
        assert billing.calculate_cost(6, 100) == 600.0

    def test_exactly_normal_hours(self):
        billing = OvertimeBilling()
        assert billing.calculate_cost(8, 100) == 800.0

    def test_overtime_hours(self):
        billing = OvertimeBilling()
        # 8 * 100 + 2 * 100 * 1.5 = 800 + 300 = 1100
        assert billing.calculate_cost(10, 100) == 1100.0

    def test_negative_rate_raises(self):
        billing = OvertimeBilling()
        with pytest.raises(ValueError):
            billing.calculate_cost(5, -10)


class TestFixedPriceBilling:
    """Тести для фіксованої вартості."""

    def test_fixed_ignores_hours(self):
        billing = FixedPriceBilling()
        assert billing.calculate_cost(100, 5000) == 5000.0

    def test_fixed_zero_rate(self):
        billing = FixedPriceBilling()
        assert billing.calculate_cost(10, 0) == 0.0

    def test_fixed_negative_rate_raises(self):
        billing = FixedPriceBilling()
        with pytest.raises(ValueError):
            billing.calculate_cost(10, -100)


class TestBillingContext:
    """Тести для контексту стратегії."""

    def test_switch_strategy_at_runtime(self):
        ctx = BillingContext(StandardBilling())
        assert ctx.execute(10, 100) == 1000.0

        ctx.strategy = OvertimeBilling()
        # 8*100 + 2*100*1.5 = 1100
        assert ctx.execute(10, 100) == 1100.0
