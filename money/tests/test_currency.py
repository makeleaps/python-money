from money.money import Currency

currency = Currency(
    code="ABC",
    numeric="1000",
    name="ABC Currency",
    symbol="$",
    decimals=2,
    countries=["My Country"],
)


def test_currency_equality() -> None:
    """
    The currency 3-letter code is what makes something unique
    """
    assert currency == Currency(
        code="ABC",
        numeric="1001",
        name="ABC Currency (Same numeric code)",
        symbol="#",
        decimals=1,
        countries=["My Country 2"],
    )


def test_currency_inequality() -> None:
    """
    The currency 3-letter code is what makes something unique
    """
    assert currency != Currency(
        code="BCD",
        numeric="1000",
        name="My Currency",
        symbol="$",
        decimals=2,
        countries=["My Country"],
    )


def test_currency_equality_against_string() -> None:
    """
    The currency can be compared to a string
    """
    assert currency == "ABC"
    assert currency != "DEF"

    assert currency == "ABC"
    assert currency != "DEF"


def test_currency_equality_against_other() -> None:
    """
    The currency can't (currently) be compared to something else...
    """

    assert currency != 1000
