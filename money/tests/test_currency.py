from money.money import Currency


def test_currency_equality() -> None:
    """
    The currency 3-letter code is what makes something unique
    """
    curr1 = Currency(
        code="ABC",
        numeric="1000",
        name="ABC Currency",
        symbol="$",
        decimals=2,
        countries=["My Country"],
    )

    curr2 = Currency(
        code="ABC",
        numeric="1001",
        name="ABC Currency (Same numeric code)",
        symbol="#",
        decimals=1,
        countries=["My Country 2"],
    )

    assert curr1 == curr2


def test_currency_inequality() -> None:
    """
    The currency 3-letter code is what makes something unique
    """
    curr1 = Currency(
        code="ABC",
        numeric="1000",
        name="My Currency",
        symbol="$",
        decimals=2,
        countries=["My Country"],
    )

    curr2 = Currency(
        code="BCD",
        numeric="1000",
        name="My Currency",
        symbol="$",
        decimals=2,
        countries=["My Country"],
    )

    assert curr1 != curr2


def test_currency_equality_against_string() -> None:
    """
    The currency can be compared to a string
    """
    curr1 = Currency(
        code="ABC",
        numeric="1000",
        name="ABC Currency",
        symbol="$",
        decimals=2,
        countries=["My Country"],
    )

    assert curr1 == "ABC"
    assert curr1 != "DEF"

    assert curr1 == "ABC"
    assert curr1 != "DEF"


def test_currency_equality_against_other() -> None:
    """
    The currency can't (currently) be compared to something else...
    """
    curr1 = Currency(
        code="ABC",
        numeric="1000",
        name="ABC Currency",
        symbol="$",
        decimals=2,
        countries=["My Country"],
    )

    assert curr1 != 1000
