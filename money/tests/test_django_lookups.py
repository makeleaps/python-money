from decimal import Decimal

import pytest
from django.db.models import Model, Q, QuerySet

from money.money import Money
from money.tests.models import (
    MoneyModelWithCustomManager,
    NullableMoneyModel,
    SimpleMoneyModel,
)

# Common Money objects used across tests
USD0 = Money(0, "USD")
EUR0 = Money(0, "EUR")
JPY0 = Money(0, "JPY")

USD50 = Money(50, "USD")
EUR50 = Money(50, "EUR")
JPY50 = Money(50, "JPY")

USD100 = Money(100, "USD")
EUR100 = Money(100, "EUR")
JPY100 = Money(100, "JPY")

USD150 = Money(150, "USD")
EUR150 = Money(150, "EUR")
JPY150 = Money(150, "JPY")

USD200 = Money(200, "USD")
EUR200 = Money(200, "EUR")
JPY200 = Money(200, "JPY")


def get_names(_queryset: QuerySet[Model]) -> tuple[str, ...]:
    return tuple(_queryset.order_by("pk").values_list("name", flat=True))


@pytest.mark.django_db
def test_lookup_with_money() -> None:
    SimpleMoneyModel.objects.create(name="USD100", price=USD100)
    SimpleMoneyModel.objects.create(name="USD101", price=USD100 + 1)
    SimpleMoneyModel.objects.create(name="USD99", price=USD100 - 1)

    SimpleMoneyModel.objects.create(name="EUR100", price=EUR100)
    SimpleMoneyModel.objects.create(name="EUR101", price=EUR100 + 1)
    SimpleMoneyModel.objects.create(name="EUR99", price=EUR100 - 1)

    SimpleMoneyModel.objects.create(name="JPY100", price=JPY100)
    SimpleMoneyModel.objects.create(name="JPY101", price=JPY100 + 1)
    SimpleMoneyModel.objects.create(name="JPY99", price=JPY100 - 1)

    # Exact:
    queryset = SimpleMoneyModel.objects.filter(price__exact=USD100)
    assert get_names(queryset) == ("USD100",)
    queryset = SimpleMoneyModel.objects.filter(price__exact=EUR100)
    assert get_names(queryset) == ("EUR100",)
    queryset = SimpleMoneyModel.objects.filter(price__exact=JPY100)
    assert get_names(queryset) == ("JPY100",)

    # Direct equal:
    queryset = SimpleMoneyModel.objects.filter(price=USD100)
    assert get_names(queryset) == ("USD100",)
    queryset = SimpleMoneyModel.objects.filter(price=EUR100)
    assert get_names(queryset) == ("EUR100",)
    queryset = SimpleMoneyModel.objects.filter(price=JPY100)
    assert get_names(queryset) == ("JPY100",)

    # Less than:
    queryset = SimpleMoneyModel.objects.filter(price__lt=USD100)
    assert get_names(queryset) == ("USD99",)
    queryset = SimpleMoneyModel.objects.filter(price__lt=EUR100)
    assert get_names(queryset) == ("EUR99",)
    queryset = SimpleMoneyModel.objects.filter(price__lt=JPY100)
    assert get_names(queryset) == ("JPY99",)

    # Greater than:
    queryset = SimpleMoneyModel.objects.filter(price__gt=USD100)
    assert get_names(queryset) == ("USD101",)
    queryset = SimpleMoneyModel.objects.filter(price__gt=EUR100)
    assert get_names(queryset) == ("EUR101",)
    queryset = SimpleMoneyModel.objects.filter(price__gt=JPY100)
    assert get_names(queryset) == ("JPY101",)

    # Less than or equal:
    queryset = SimpleMoneyModel.objects.filter(price__lte=USD100)
    assert get_names(queryset) == ("USD100", "USD99")
    queryset = SimpleMoneyModel.objects.filter(price__lte=EUR100)
    assert get_names(queryset) == ("EUR100", "EUR99")
    queryset = SimpleMoneyModel.objects.filter(price__lte=JPY100)
    assert get_names(queryset) == ("JPY100", "JPY99")

    # Greater than or equal:
    queryset = SimpleMoneyModel.objects.filter(price__gte=USD100)
    assert get_names(queryset) == ("USD100", "USD101")
    queryset = SimpleMoneyModel.objects.filter(price__gte=EUR100)
    assert get_names(queryset) == ("EUR100", "EUR101")
    queryset = SimpleMoneyModel.objects.filter(price__gte=JPY100)
    assert get_names(queryset) == ("JPY100", "JPY101")


@pytest.mark.django_db
def test_lookup_with_custom_manager() -> None:
    MoneyModelWithCustomManager.objects.create(name="USD100", price=USD100)
    MoneyModelWithCustomManager.objects.create(name="USD101", price=USD100 + 1)
    MoneyModelWithCustomManager.objects.create(name="USD99", price=USD100 - 1)

    MoneyModelWithCustomManager.objects.create(name="EUR100", price=EUR100)
    MoneyModelWithCustomManager.objects.create(name="EUR101", price=EUR100 + 1)
    MoneyModelWithCustomManager.objects.create(name="EUR99", price=EUR100 - 1)

    MoneyModelWithCustomManager.objects.create(name="JPY100", price=JPY100)
    MoneyModelWithCustomManager.objects.create(name="JPY101", price=JPY100 + 1)
    MoneyModelWithCustomManager.objects.create(name="JPY99", price=JPY100 - 1)

    # Exact:
    queryset = MoneyModelWithCustomManager.objects.filter(price__exact=USD100)
    assert get_names(queryset) == ("USD100",)
    queryset = MoneyModelWithCustomManager.objects.filter(price__exact=EUR100)
    assert get_names(queryset) == ("EUR100",)
    queryset = MoneyModelWithCustomManager.objects.filter(price__exact=JPY100)
    assert get_names(queryset) == ("JPY100",)

    # Direct equal:
    queryset = MoneyModelWithCustomManager.objects.filter(price=USD100)
    assert get_names(queryset) == ("USD100",)
    queryset = MoneyModelWithCustomManager.objects.filter(price=EUR100)
    assert get_names(queryset) == ("EUR100",)
    queryset = MoneyModelWithCustomManager.objects.filter(price=JPY100)
    assert get_names(queryset) == ("JPY100",)

    # Less than:
    queryset = MoneyModelWithCustomManager.objects.filter(price__lt=USD100)
    assert get_names(queryset) == ("USD99",)
    queryset = MoneyModelWithCustomManager.objects.filter(price__lt=EUR100)
    assert get_names(queryset) == ("EUR99",)
    queryset = MoneyModelWithCustomManager.objects.filter(price__lt=JPY100)
    assert get_names(queryset) == ("JPY99",)

    # Greater than:
    queryset = MoneyModelWithCustomManager.objects.filter(price__gt=USD100)
    assert get_names(queryset) == ("USD101",)
    queryset = MoneyModelWithCustomManager.objects.filter(price__gt=EUR100)
    assert get_names(queryset) == ("EUR101",)
    queryset = MoneyModelWithCustomManager.objects.filter(price__gt=JPY100)
    assert get_names(queryset) == ("JPY101",)

    # Less than or equal:
    queryset = MoneyModelWithCustomManager.objects.filter(price__lte=USD100)
    assert get_names(queryset) == ("USD100", "USD99")
    queryset = MoneyModelWithCustomManager.objects.filter(price__lte=EUR100)
    assert get_names(queryset) == ("EUR100", "EUR99")
    queryset = MoneyModelWithCustomManager.objects.filter(price__lte=JPY100)
    assert get_names(queryset) == ("JPY100", "JPY99")

    # Greater than or equal:
    queryset = MoneyModelWithCustomManager.objects.filter(price__gte=USD100)
    assert get_names(queryset) == ("USD100", "USD101")
    queryset = MoneyModelWithCustomManager.objects.filter(price__gte=EUR100)
    assert get_names(queryset) == ("EUR100", "EUR101")
    queryset = MoneyModelWithCustomManager.objects.filter(price__gte=JPY100)
    assert get_names(queryset) == ("JPY100", "JPY101")

    # Custom Manager:
    queryset = MoneyModelWithCustomManager.objects.only_usd()
    assert get_names(queryset) == ("USD100", "USD101", "USD99")
    queryset = MoneyModelWithCustomManager.objects.only_usd(price__lte=USD100)
    assert get_names(queryset) == ("USD100", "USD99")
    queryset = MoneyModelWithCustomManager.objects.only_usd(price__lte=EUR100)
    assert get_names(queryset) == tuple()


@pytest.mark.django_db
def test_currency_isolation() -> None:
    """Test that lookups properly isolate by currency."""
    # Create records with same amount but different currencies
    SimpleMoneyModel.objects.create(name="USD50", price=USD50)
    SimpleMoneyModel.objects.create(name="EUR50", price=EUR50)
    SimpleMoneyModel.objects.create(name="JPY50", price=JPY50)

    # Exact lookup should only match the specific currency
    queryset = SimpleMoneyModel.objects.filter(price=USD50)
    assert get_names(queryset) == ("USD50",)

    queryset = SimpleMoneyModel.objects.filter(price=EUR50)
    assert get_names(queryset) == ("EUR50",)

    queryset = SimpleMoneyModel.objects.filter(price=JPY50)
    assert get_names(queryset) == ("JPY50",)

    # Greater than should only compare within same currency
    SimpleMoneyModel.objects.create(name="USD100", price=USD100)
    SimpleMoneyModel.objects.create(name="EUR100", price=EUR100)

    queryset = SimpleMoneyModel.objects.filter(price__gt=USD50)
    assert get_names(queryset) == ("USD100",)

    queryset = SimpleMoneyModel.objects.filter(price__gt=EUR50)
    assert get_names(queryset) == ("EUR100",)


@pytest.mark.django_db
def test_decimal_precision() -> None:
    """Test lookups with various decimal precision values."""
    SimpleMoneyModel.objects.create(name="precise1", price=Money("100.123", "USD"))
    SimpleMoneyModel.objects.create(name="precise2", price=Money("100.456", "USD"))
    SimpleMoneyModel.objects.create(name="precise3", price=Money("100.789", "USD"))

    # Exact match with decimal precision
    queryset = SimpleMoneyModel.objects.filter(price=Money("100.123", "USD"))
    assert get_names(queryset) == ("precise1",)

    # Less than with decimal
    queryset = SimpleMoneyModel.objects.filter(price__lt=Money("100.5", "USD"))
    assert get_names(queryset) == ("precise1", "precise2")

    # Greater than or equal with decimal
    queryset = SimpleMoneyModel.objects.filter(price__gte=Money("100.456", "USD"))
    assert get_names(queryset) == ("precise2", "precise3")


@pytest.mark.django_db
def test_zero_values() -> None:
    """Test lookups with zero amounts across different currencies."""
    SimpleMoneyModel.objects.create(name="USD0", price=USD0)
    SimpleMoneyModel.objects.create(name="EUR0", price=EUR0)
    SimpleMoneyModel.objects.create(name="JPY0", price=JPY0)
    SimpleMoneyModel.objects.create(name="USD50", price=USD50)
    SimpleMoneyModel.objects.create(name="EUR50", price=EUR50)

    # Exact zero lookup
    queryset = SimpleMoneyModel.objects.filter(price=USD0)
    assert get_names(queryset) == ("USD0",)

    # Greater than zero
    queryset = SimpleMoneyModel.objects.filter(price__gt=USD0)
    assert get_names(queryset) == ("USD50",)

    # Less than or equal to zero
    queryset = SimpleMoneyModel.objects.filter(price__lte=EUR0)
    assert get_names(queryset) == ("EUR0",)


@pytest.mark.django_db
def test_negative_values() -> None:
    """Test lookups with negative amounts."""
    SimpleMoneyModel.objects.create(name="neg50", price=Money(-50, "USD"))
    SimpleMoneyModel.objects.create(name="zero", price=USD0)
    SimpleMoneyModel.objects.create(name="pos50", price=USD50)

    # Less than zero
    queryset = SimpleMoneyModel.objects.filter(price__lt=USD0)
    assert get_names(queryset) == ("neg50",)

    # Greater than negative value
    queryset = SimpleMoneyModel.objects.filter(price__gt=Money(-50, "USD"))
    assert get_names(queryset) == ("zero", "pos50")

    # Exact negative match
    queryset = SimpleMoneyModel.objects.filter(price=Money(-50, "USD"))
    assert get_names(queryset) == ("neg50",)


@pytest.mark.django_db
def test_nullable_field() -> None:
    """Test lookups with nullable money fields."""
    NullableMoneyModel.objects.create(name="null_price", price=None)
    NullableMoneyModel.objects.create(name="has_price", price=USD100)

    # isnull lookup
    queryset = NullableMoneyModel.objects.filter(price__isnull=True)
    assert get_names(queryset) == ("null_price",)

    queryset = NullableMoneyModel.objects.filter(price__isnull=False)
    assert get_names(queryset) == ("has_price",)

    # Exact lookup with None should not match anything
    queryset = NullableMoneyModel.objects.filter(price=USD100)
    assert get_names(queryset) == ("has_price",)


@pytest.mark.django_db
def test_chained_filters() -> None:
    """Test multiple chained filter operations."""
    SimpleMoneyModel.objects.create(name="USD50", price=USD50)
    SimpleMoneyModel.objects.create(name="USD100", price=USD100)
    SimpleMoneyModel.objects.create(name="USD150", price=USD150)
    SimpleMoneyModel.objects.create(name="EUR100", price=EUR100)

    # Chain gte and lte
    queryset = SimpleMoneyModel.objects.filter(price__gte=USD50).filter(
        price__lte=USD100
    )
    assert get_names(queryset) == ("USD50", "USD100")

    # Chain with multiple currencies
    queryset = SimpleMoneyModel.objects.filter(
        price__gte=USD100
    ) | SimpleMoneyModel.objects.filter(price__gte=EUR100)
    assert get_names(queryset) == ("USD100", "USD150", "EUR100")


@pytest.mark.django_db
def test_q_objects() -> None:
    """Test lookups with Q objects for complex queries."""
    SimpleMoneyModel.objects.create(name="USD50", price=USD50)
    SimpleMoneyModel.objects.create(name="USD100", price=USD100)
    SimpleMoneyModel.objects.create(name="EUR50", price=EUR50)
    SimpleMoneyModel.objects.create(name="EUR100", price=EUR100)

    # OR condition
    queryset = SimpleMoneyModel.objects.filter(Q(price=USD50) | Q(price=EUR100))
    assert get_names(queryset) == ("USD50", "EUR100")

    # AND condition
    queryset = SimpleMoneyModel.objects.filter(
        Q(price__gte=USD50) & Q(price__lte=USD100)
    )
    assert get_names(queryset) == ("USD50", "USD100")

    # NOT condition
    queryset = SimpleMoneyModel.objects.filter(~Q(price=USD50))
    assert get_names(queryset) == ("USD100", "EUR50", "EUR100")


@pytest.mark.django_db
def test_exclude_operations() -> None:
    """Test exclude operations with money lookups."""
    SimpleMoneyModel.objects.create(name="USD50", price=USD50)
    SimpleMoneyModel.objects.create(name="USD100", price=USD100)
    SimpleMoneyModel.objects.create(name="EUR50", price=EUR50)

    # Exclude exact value
    queryset = SimpleMoneyModel.objects.exclude(price=USD50)
    assert get_names(queryset) == ("USD100", "EUR50")

    # Exclude with comparison
    queryset = SimpleMoneyModel.objects.exclude(price__lt=USD100)
    assert get_names(queryset) == ("USD100", "EUR50")

    # Exclude with gte
    queryset = SimpleMoneyModel.objects.exclude(price__gte=USD100)
    assert get_names(queryset) == ("USD50", "EUR50")


@pytest.mark.django_db
def test_lookup_with_decimal() -> None:
    """Test lookups with Decimal values (should compare by amount only, ignores currency)."""
    SimpleMoneyModel.objects.create(name="USD50", price=USD50)
    SimpleMoneyModel.objects.create(name="EUR100", price=EUR100)
    SimpleMoneyModel.objects.create(name="USD100", price=USD100)
    SimpleMoneyModel.objects.create(name="JPY150", price=JPY150)
    SimpleMoneyModel.objects.create(name="EUR200", price=EUR200)

    # Direct equal - matches all currencies with amount 100
    queryset = SimpleMoneyModel.objects.filter(price=Decimal("100"))
    assert get_names(queryset) == ("EUR100", "USD100")

    # Exact lookup
    queryset = SimpleMoneyModel.objects.filter(price__exact=Decimal("100"))
    assert get_names(queryset) == ("EUR100", "USD100")

    # Less than
    queryset = SimpleMoneyModel.objects.filter(price__lt=Decimal("100"))
    assert get_names(queryset) == ("USD50",)

    # Less than or equal
    queryset = SimpleMoneyModel.objects.filter(price__lte=Decimal("100"))
    assert get_names(queryset) == ("USD50", "EUR100", "USD100")

    # Greater than
    queryset = SimpleMoneyModel.objects.filter(price__gt=Decimal("100"))
    assert get_names(queryset) == ("JPY150", "EUR200")

    # Greater than or equal
    queryset = SimpleMoneyModel.objects.filter(price__gte=Decimal("100"))
    assert get_names(queryset) == ("EUR100", "USD100", "JPY150", "EUR200")

    # Decimal with precision
    SimpleMoneyModel.objects.create(name="USD99.99", price=Money("99.99", "USD"))
    queryset = SimpleMoneyModel.objects.filter(price__lt=Decimal("100"))
    assert get_names(queryset) == ("USD50", "USD99.99")


@pytest.mark.django_db
def test_lookup_with_int() -> None:
    """Test lookups with int values (should compare by amount only, ignores currency)."""
    SimpleMoneyModel.objects.create(name="USD50", price=USD50)
    SimpleMoneyModel.objects.create(name="EUR100", price=EUR100)
    SimpleMoneyModel.objects.create(name="USD100", price=USD100)
    SimpleMoneyModel.objects.create(name="JPY150", price=JPY150)
    SimpleMoneyModel.objects.create(name="EUR200", price=EUR200)

    # Direct equal - matches all currencies with amount 100
    queryset = SimpleMoneyModel.objects.filter(price=100)
    assert get_names(queryset) == ("EUR100", "USD100")

    # Exact lookup
    queryset = SimpleMoneyModel.objects.filter(price__exact=100)
    assert get_names(queryset) == ("EUR100", "USD100")

    # Less than
    queryset = SimpleMoneyModel.objects.filter(price__lt=100)
    assert get_names(queryset) == ("USD50",)

    # Less than or equal
    queryset = SimpleMoneyModel.objects.filter(price__lte=100)
    assert get_names(queryset) == ("USD50", "EUR100", "USD100")

    # Greater than
    queryset = SimpleMoneyModel.objects.filter(price__gt=100)
    assert get_names(queryset) == ("JPY150", "EUR200")

    # Greater than or equal
    queryset = SimpleMoneyModel.objects.filter(price__gte=100)
    assert get_names(queryset) == ("EUR100", "USD100", "JPY150", "EUR200")

    # Zero value
    SimpleMoneyModel.objects.create(name="JPY0", price=JPY0)
    queryset = SimpleMoneyModel.objects.filter(price__lte=0)
    assert get_names(queryset) == ("JPY0",)


@pytest.mark.django_db
def test_lookup_with_float() -> None:
    """Test lookups with float values (should compare by amount only, ignores currency)."""
    SimpleMoneyModel.objects.create(name="USD50.5", price=Money("50.5", "USD"))
    SimpleMoneyModel.objects.create(name="EUR100.0", price=Money("100.0", "EUR"))
    SimpleMoneyModel.objects.create(name="USD100.5", price=Money("100.5", "USD"))
    SimpleMoneyModel.objects.create(name="JPY150.75", price=Money("150.75", "JPY"))
    SimpleMoneyModel.objects.create(name="EUR200.25", price=Money("200.25", "EUR"))

    # Direct equal - matches all currencies with amount 100.0
    queryset = SimpleMoneyModel.objects.filter(price=100.0)
    assert get_names(queryset) == ("EUR100.0",)

    # Exact lookup
    queryset = SimpleMoneyModel.objects.filter(price__exact=100.5)
    assert get_names(queryset) == ("USD100.5",)

    # Less than
    queryset = SimpleMoneyModel.objects.filter(price__lt=100.0)
    assert get_names(queryset) == ("USD50.5",)

    # Less than or equal
    queryset = SimpleMoneyModel.objects.filter(price__lte=100.5)
    assert get_names(queryset) == ("USD50.5", "EUR100.0", "USD100.5")

    # Greater than
    queryset = SimpleMoneyModel.objects.filter(price__gt=100.5)
    assert get_names(queryset) == ("JPY150.75", "EUR200.25")

    # Greater than or equal
    queryset = SimpleMoneyModel.objects.filter(price__gte=150.75)
    assert get_names(queryset) == ("JPY150.75", "EUR200.25")

    # Float with small precision differences
    SimpleMoneyModel.objects.create(name="USD99.99", price=Money("99.99", "USD"))
    SimpleMoneyModel.objects.create(name="USD100.01", price=Money("100.01", "USD"))
    queryset = SimpleMoneyModel.objects.filter(price__gt=99.99)
    assert get_names(queryset) == (
        "EUR100.0",
        "USD100.5",
        "JPY150.75",
        "EUR200.25",
        "USD100.01",
    )


@pytest.mark.django_db
def test_multiple_same_amount_different_currencies() -> None:
    """Test that multiple records with same amount but different currencies are handled correctly."""
    # Create 3 records with amount 100 in different currencies
    SimpleMoneyModel.objects.create(name="USD100", price=USD100)
    SimpleMoneyModel.objects.create(name="EUR100", price=EUR100)
    SimpleMoneyModel.objects.create(name="JPY100", price=JPY100)

    # Each currency lookup should return exactly one record
    for money_obj, expected_name in [
        (USD100, "USD100"),
        (EUR100, "EUR100"),
        (JPY100, "JPY100"),
    ]:
        queryset = SimpleMoneyModel.objects.filter(price=money_obj)
        assert get_names(queryset) == (expected_name,)


@pytest.mark.django_db
def test_lookup_with_only_currency() -> None:
    """Test that lookup with price_currency works"""
    # Create 3 records with amount 100 in different currencies
    SimpleMoneyModel.objects.create(name="USD100", price=USD100)
    SimpleMoneyModel.objects.create(name="EUR100", price=EUR100)
    SimpleMoneyModel.objects.create(name="JPY100", price=JPY100)

    # Create 3 records with amount 200 in different currencies
    SimpleMoneyModel.objects.create(name="USD200", price=USD200)
    SimpleMoneyModel.objects.create(name="EUR200", price=EUR200)
    SimpleMoneyModel.objects.create(name="JPY200", price=JPY200)

    # Each currency lookup should return exactly one record
    for currency, expected_names in [
        ("USD", ("USD100", "USD200")),
        ("EUR", ("EUR100", "EUR200")),
        ("JPY", ("JPY100", "JPY200")),
    ]:
        queryset = SimpleMoneyModel.objects.filter(price_currency=currency)
        assert get_names(queryset) == expected_names
