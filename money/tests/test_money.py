from decimal import Decimal

import pytest

from money.exceptions import IncorrectMoneyInputError
from money.money import CURRENCY, Currency, Money


def test_string_parse() -> None:
    value = Money.from_string("USD 100.0")
    assert value.amount == Decimal("100.0")
    assert value.currency == "USD"
    assert value.currency == CURRENCY["USD"]


def test_string_parse_default_currency() -> None:
    value = Money.from_string("100.0")
    assert value.amount == Decimal("100.0")
    assert value.currency == "XXX"
    assert value.currency == CURRENCY["XXX"]


def test_creation() -> None:
    """
    We should be able to create a money object with inputs
    similar to a Decimal type
    """
    result = Money(10, "USD")
    assert result.amount == 10

    result = Money(-10, "USD")
    assert result.amount == Decimal("-10")

    result = Money(Decimal("10"), "USD")
    assert result.amount == Decimal("10")

    result = Money(Decimal("-10"), "USD")
    assert result.amount == Decimal("-10")

    result = Money("10.50", "USD")
    assert result.amount == Decimal("10.50")

    result = Money("-10.50", "USD")
    assert result.amount == Decimal("-10.50")

    result = Money("10.50", "USD")
    assert result.amount == Decimal("10.50")

    result = Money("-10.50", "USD")
    assert result.amount == Decimal("-10.50")


def test_creation_unspecified_currency() -> None:
    """
    Same thing as above but with the unspecified 'xxx' currency
    """

    result = Money(10)
    assert result.amount == 10

    result = Money(-10)
    assert result.amount == Decimal("-10")

    result = Money(Decimal("10"))
    assert result.amount == Decimal("10")

    result = Money(Decimal("-10"))
    assert result.amount == Decimal("-10")

    result = Money("10.50")
    assert result.amount == Decimal("10.50")

    result = Money("-10.50")
    assert result.amount == Decimal("-10.50")


def test_creation_unspecified_amount() -> None:
    """
    Same thing as above but with the unspecified 'xxx' currency
    """

    result = Money(currency="USD")
    assert result.amount == 0
    assert result.currency.code == "USD"


def test_creation_internal_types() -> None:
    curr = Currency(code="AAA", name="My Currency")
    result = Money(Decimal("777"), currency=curr)
    assert result.amount == Decimal("777")
    assert result.currency.code == "AAA"
    assert result.currency.name == "My Currency"


def test_creation_parsed() -> None:
    result = Money("XXX -10.50")
    assert result.amount == Decimal("-10.50")
    assert result.currency.code == "XXX"

    result = Money("USD -11.50")
    assert result.amount == Decimal("-11.50")
    assert result.currency.code == "USD"

    result = Money("JPY -12.50")
    assert result.amount == Decimal("-12.50")
    assert result.currency.code == "JPY"


def test_creation_parsed_conflicting() -> None:
    # currency declaration two ways
    with pytest.raises(IncorrectMoneyInputError):
        Money("USD 123", "JPY")


def test_creation_parsed_malformed() -> None:
    with pytest.raises(IncorrectMoneyInputError):
        Money("USD 123 USD")


def test_equality() -> None:
    ten_bucks = Money(10, "USD")
    a_hamilton = Money(10, "USD")

    juu_en = Money(10, "JPY")

    nada = Money(0, "USD")

    # Scalars cannot be compared to Money class
    assert ten_bucks != 10
    # unless it is 0
    assert nada == 0

    # Money is equal to money of the same type
    assert ten_bucks == a_hamilton

    # But not different currencies
    assert ten_bucks != juu_en


def test_subtraction() -> None:
    result = Money(10, "USD") - Money(3, "USD")
    assert result == Money(7, "USD")
    assert result.amount == Decimal("7")
    assert result.currency == CURRENCY["USD"]


def test_negative_subtraction() -> None:
    result = Money(3, "USD") - Money(10, "USD")
    assert result == Money(-7, "USD")
    assert result.amount == Decimal("-7")
    assert result.currency == CURRENCY["USD"]


def test_amount_attribute() -> None:
    value = Money(101, "USD")
    assert value.amount == 101


def test_currency_attribute() -> None:
    value = Money(101, "USD")
    assert value.currency == "USD"
    value = Money(101, "JPY")
    assert value.currency == "JPY"
