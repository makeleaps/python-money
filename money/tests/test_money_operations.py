from __future__ import division, unicode_literals

from typing import Union, Callable, Optional

import pytest
from decimal import Decimal

from money.money import Money, CurrencyMismatchException


MONEY_STRINGS: list[tuple[Money, str]] = [
    # Undefined currency:
    (Money(" 123"), "XXX 123"),
    (Money("-123"), "XXX -123"),
    # Test a currency with decimals:
    (Money(" 123", "USD"), "USD 123"),
    (Money("-123", "USD"), "USD -123"),
    (Money(" 123.0000", "USD"), "USD 123.0000"),
    (Money("-123.0000", "USD"), "USD -123.0000"),
    (Money(" 123.25", "USD"), "USD 123.25"),
    (Money("-123.25", "USD"), "USD -123.25"),
    # Test a currency that is normally written without decimals:
    (Money(" 123", "JPY"), "JPY 123"),
    (Money("-123", "JPY"), "JPY -123"),
    (Money(" 123.0000", "JPY"), "JPY 123.0000"),
    (Money("-123.0000", "JPY"), "JPY -123.0000"),
    (Money(" 123.25", "JPY"), "JPY 123.25"),
    (Money("-123.25", "JPY"), "JPY -123.25"),
]


@pytest.mark.parametrize("value,expected", MONEY_STRINGS)
def test_str(value: Money, expected: str) -> None:
    assert str(value) == expected


@pytest.mark.parametrize("value,expected", MONEY_STRINGS)
def test_repr(value: Money, expected: str) -> None:
    assert repr(value) == expected


Value = Optional[Union[Money, Decimal, float, int]]
ArithmeticFunc = Callable[[], Value]

MONEY_ARITHMETIC: list[tuple[ArithmeticFunc, Value]] = [
    # Casting
    (lambda: Money("100") + 0.5, Money("100.5")),
    (lambda: float(Money("100")), float(100)),
    (lambda: int(Money("100")), 100),
    # Addition
    (lambda: Money("100") + Money("100"), Money("200")),
    (lambda: Money("100") + Money("-100"), Money("0")),
    (lambda: Money("100") + 100, Money("200")),
    (lambda: Money("100") + -100, Money("0")),
    (lambda: Money("100") + Decimal("100"), Money("200")),
    (lambda: Money("100") + Decimal("-100"), Money("0")),
    # Subtraction
    (lambda: Money("100") - Money("100"), Money("0")),
    (lambda: Money("100") - Money("-100"), Money("200")),
    (lambda: Money("100") - 100, Money("0")),
    (lambda: Money("100") - -100, Money("200")),
    (lambda: Money("100") - Decimal("100"), Money("0")),
    (lambda: Money("100") - Decimal("-100"), Money("200")),
    # Multiplication
    (lambda: Money("100") * 4, Money("400")),
    (lambda: Money("100") * Decimal("4"), Money("400")),
    # Division
    (lambda: Money("100") / 4, Money("25")),  # type: ignore[no-any-return]
    (lambda: Money("100") / Decimal("4"), Money("25")),
    # Negation
    (lambda: -Money("100"), Money("-100")),
    (lambda: -Money("100.12", "USD"), Money("-100.12", "USD")),
    (lambda: +Money("100"), Money("100")),
]


@pytest.mark.parametrize("value,expected", MONEY_ARITHMETIC)
def test_arithmetic(value: ArithmeticFunc, expected: Value) -> None:
    result = value()
    assert result == expected


MONEY_ARITHMETIC_UNSUPPORTED: list[ArithmeticFunc] = [
    # Modulus
    (lambda: 4 % Money("100")),
    (lambda: Decimal("4") % Money("100")),
    (lambda: Money("100") % 4),
    (lambda: Money("100") % Decimal("4")),
    # Division: floor division (see future import above)
    (lambda: Money("100") // 4),
    (lambda: Money("100") // Decimal("4")),
    # Dividing a value by Money
    (lambda: 4 / Money("100")),
    (lambda: Decimal("4") / Money("100")),
    (lambda: Money("100") / Money("100")),
    # Multiplication of 2 Money objects
    (lambda: Money("100") * Money("100")),
    # Subtracting money from a digit
    # (lambda: 100 - Money('100')),
    # (lambda: 100 - - Money('100')),
    (lambda: Decimal("100") - Money("100")),
    (lambda: Decimal("-100") - Money("100")),
]


@pytest.mark.parametrize("value", MONEY_ARITHMETIC_UNSUPPORTED)
def test_invalid_arithmetic(value: ArithmeticFunc) -> None:
    with pytest.raises(TypeError):
        value()


MONEY_ARITHMETIC_MISMATCHED: list[ArithmeticFunc] = [
    # Mismatched currencies
    (lambda: Money("100", "JPY") + Money("100", "EUR")),
    (lambda: Money("100", "JPY") - Money("100", "EUR")),
]


@pytest.mark.parametrize("value", MONEY_ARITHMETIC_MISMATCHED)
def test_invalid_currency(value: ArithmeticFunc) -> None:
    with pytest.raises(CurrencyMismatchException):
        value()


MONEY_EQUALITY: list[tuple[bool, bool]] = [
    # Bool
    (bool(Money("0")), False),
    (bool(Money("1")), True),
    (bool(Money("0", "EUR")), False),
    (bool(Money("1", "EUR")), True),
    (bool(Money("-1", "EUR")), True),
    # Equality
    (Money("0") == Money("0"), True),
    (Money("100") == Money("100"), True),
    (Money("-100") == Money("-100"), True),
    (Money("100", "EUR") == Money("100", "EUR"), True),
    (Money("100.0", "EUR") == Money("100", "EUR"), True),
    # Mismatched currencies
    (Money("0", "EUR") == Money("0", "JPY"), False),
    (Money("100", "EUR") == Money("100"), False),
    (Money("100", "EUR") == Money("100", "JPY"), False),
    (Money("100.0", "EUR") == Money("100", "JPY"), False),
    # Other types
    (Money("100.0", "EUR") == Decimal("100"), False),
    (Money("100.0", "EUR") == 100, False),
    (Decimal("100") == Money("100.0", "EUR"), False),
    (100 == Money("100.0", "EUR"), False),
    # Inequality
    (Money("0") != Money("0"), False),
    (Money("100") != Money("100"), False),
    (Money("-100") != Money("-100"), False),
    (Money("100", "EUR") != Money("100", "EUR"), False),
    (Money("100.0", "EUR") != Money("100", "EUR"), False),
    # Mismatched currencies
    (Money("0", "EUR") != Money("0", "JPY"), True),
    (Money("100", "EUR") != Money("100"), True),
    (Money("100", "EUR") != Money("100", "JPY"), True),
    (Money("100.0", "EUR") != Money("100", "JPY"), True),
    # Other types
    (Money("100.0", "EUR") != Decimal("100"), True),
    (Money("100.0", "EUR") != 100, True),
    (Decimal("100") != Money("100.0", "EUR"), True),
    (100 != Money("100.0", "EUR"), True),
    # LT/GT
    (0 < Money("0"), False),
    (100 < Money("100"), False),
    (-100 < Money("-100"), False),
    (100 < Money("100", "EUR"), False),
    (100.0 < Money("100", "EUR"), False),
    (0 > Money("1"), False),
    (1 > Money("0"), True),
    (-101 > Money("-100"), False),
    (-100 > Money("-101"), True),
    (100 > Money("100.01", "EUR"), False),
    (100.01 > Money("100", "EUR"), True),
    (Money("0") < Money("0"), False),
    (Money("100") < Money("100"), False),
    (Money("-100") < Money("-100"), False),
    (Money("100", "EUR") < Money("100", "EUR"), False),
    (Money("100.0", "EUR") < Money("100", "EUR"), False),
    (Money("0") > Money("0"), False),
    (Money("100") > Money("100"), False),
    (Money("-100") > Money("-100"), False),
    (Money("100", "EUR") > Money("100", "EUR"), False),
    (Money("0") < Money("1"), True),
    (Money("1") < Money("0"), False),
    (Money("-101") < Money("-100"), True),
    (Money("-100") < Money("-101"), False),
    (Money("100", "EUR") < Money("100.01", "EUR"), True),
    (Money("100.01", "EUR") < Money("100", "EUR"), False),
    (Money("0") > Money("1"), False),
    (Money("1") > Money("0"), True),
    (Money("-101") > Money("-100"), False),
    (Money("-100") > Money("-101"), True),
    (Money("100", "EUR") > Money("100.01", "EUR"), False),
    (Money("100.01", "EUR") > Money("100", "EUR"), True),
    (Money("100.0", "EUR") < Money("100", "EUR"), False),
    (Money("100.0", "EUR") > Money("100", "EUR"), False),
    # GTE/LTE
    (Money("0") <= Money("0"), True),
    (Money("100") <= Money("100"), True),
    (Money("-100") <= Money("-100"), True),
    (Money("100", "EUR") <= Money("100", "EUR"), True),
    (Money("100.0", "EUR") <= Money("100", "EUR"), True),
    (Money("0") >= Money("0"), True),
    (Money("100") >= Money("100"), True),
    (Money("-100") >= Money("-100"), True),
    (Money("100", "EUR") >= Money("100", "EUR"), True),
    (Money("100.0", "EUR") >= Money("100", "EUR"), True),
    (Money("0") <= Money("1"), True),
    (Money("1") <= Money("0"), False),
    (Money("-101") <= Money("-100"), True),
    (Money("-100") <= Money("-101"), False),
    (Money("100", "EUR") <= Money("100.01", "EUR"), True),
    (Money("100.01", "EUR") <= Money("100", "EUR"), False),
    (Money("0") >= Money("1"), False),
    (Money("1") >= Money("0"), True),
    (Money("-101") >= Money("-100"), False),
    (Money("-100") >= Money("-101"), True),
    (Money("100", "EUR") >= Money("100.01", "EUR"), False),
    (Money("100.01", "EUR") >= Money("100", "EUR"), True),
    (Money("100.0", "EUR") <= Money("100", "EUR"), True),
    (Money("100.0", "EUR") >= Money("100", "EUR"), True),
]


@pytest.mark.parametrize("value,expected", MONEY_EQUALITY)
def test_equality(value: bool, expected: bool) -> None:
    assert value == expected
