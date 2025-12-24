import pytest
from django.db import IntegrityError
from django.test import TestCase

from money.constants import CURRENCY
from money.dataclasses.money import Money
from money.exceptions import NotSupportedLookup
from money.tests.models import (
    MoneyModelDefaultMoneyUSD,
    MoneyModelDefaults,
    SimpleMoneyModel,
)


@pytest.mark.django_db
def test_non_null() -> None:
    instance = SimpleMoneyModel()
    with pytest.raises(IntegrityError):
        instance.save()


@pytest.mark.django_db
def test_creating() -> None:
    ind = 0
    for code, currency in CURRENCY.items():
        ind = ind + 1
        price = Money(ind * 1000.0, code)
        SimpleMoneyModel.objects.create(
            name=currency.name, price=price.amount, price_currency=price.currency
        )
    count = SimpleMoneyModel.objects.all().count()
    assert len(CURRENCY) == count

    for code in CURRENCY:
        count = SimpleMoneyModel.objects.filter(price_currency=code).count()
        assert count == 1


@pytest.mark.django_db
def test_price_from_string() -> None:
    price1 = Money("400", "USD")
    price2 = Money.from_string("USD 400")
    assert price1 == price2
    assert price1.amount == price2.amount
    assert price1.currency == price2.currency


@pytest.mark.django_db
def test_retrieve() -> None:
    price = Money(100, "USD")
    SimpleMoneyModel.objects.create(name="USD100", price=price)

    # Filter
    queryset = SimpleMoneyModel.objects.filter(price=price)
    assert queryset.count() == 1
    assert queryset[0].price == price

    # Get
    entry = SimpleMoneyModel.objects.get(price=price)
    assert entry.price == price

    # test retrieving without currency
    entry = SimpleMoneyModel.objects.get(price=100)
    assert entry.price == price


@pytest.mark.django_db
def test_assign() -> None:
    price = Money(100, "USD")
    ent = SimpleMoneyModel(
        name="test", price=price.amount, price_currency=price.currency
    )
    ent.save()
    assert ent.price == Money(100, "USD")

    ent.price = Money(10, "USD")
    ent.save()
    assert ent.price == Money(10, "USD")

    ent_same = SimpleMoneyModel.objects.get(pk=ent.id)
    assert ent_same.price == Money(10, "USD")


@pytest.mark.django_db
def test_retrieve_and_update() -> None:
    created = SimpleMoneyModel.objects.create(name="USD100", price=Money(100, "USD"))
    assert created.price == Money(100, "USD")

    ent = SimpleMoneyModel.objects.filter(price__exact=Money(100, "USD")).get()
    assert ent.price == Money(100, "USD")

    ent.price = Money(300, "USD")
    ent.save()

    ent = SimpleMoneyModel.objects.filter(price__exact=Money(300, "USD")).get()
    assert ent.price == Money(300, "USD")


@pytest.mark.django_db
def test_defaults_as_money_objects() -> None:
    ent = MoneyModelDefaultMoneyUSD.objects.create(name="123.45 USD")
    assert ent.price == Money("123.45", "USD")

    ent = MoneyModelDefaultMoneyUSD.objects.get(pk=ent.id)
    assert ent.price == Money("123.45", "USD")


@pytest.mark.django_db
def test_defaults_as_separate_values() -> None:
    ent = MoneyModelDefaults.objects.create(name="100 USD", price=100)
    assert ent.price == Money(100, "USD")

    ent = MoneyModelDefaults.objects.get(pk=ent.id)
    assert ent.price == Money(100, "USD")


@pytest.mark.django_db
def test_price_attribute() -> None:
    e = SimpleMoneyModel()
    e.price = Money(3, "BGN")
    assert e.price == Money(3, "BGN")

    e.price = Money.from_string("BGN 5.0")
    assert e.price == Money(5, "BGN")


@pytest.mark.django_db
def test_price_attribute_in_constructor() -> None:
    e1 = SimpleMoneyModel(price=Money(100, "USD"))
    e2 = SimpleMoneyModel(price=Money(200, "JPY"))
    assert e1.price == Money(100, "USD")
    assert e2.price == Money(200, "JPY")


@pytest.mark.django_db
def test_price_attribute_update() -> None:
    e2 = SimpleMoneyModel(price=Money(200, "JPY"))
    e2.price = Money(300, "USD")
    assert e2.price == Money(300, "USD")


@pytest.mark.django_db
def test_price_amount_to_string() -> None:
    e1 = SimpleMoneyModel(price=Money("200", "JPY"))
    e2 = SimpleMoneyModel(price=Money("200.0", "JPY"))

    assert str(e1.price) == "JPY 200"

    assert str(e1.price.amount) == "200"

    assert str(e2.price.amount) == "200.0"


@pytest.mark.django_db
def test_price_amount_to_string_non_money() -> None:
    e1 = MoneyModelDefaults()

    assert str(e1.price) == "USD 123.45"

    assert str(e1.price.amount) == "123.45"


@pytest.mark.django_db
def test_zero_edge_case() -> None:
    created = SimpleMoneyModel.objects.create(
        name="zero dollars", price=Money(0, "USD")
    )
    assert created.price == Money(0, "USD")

    ent = SimpleMoneyModel.objects.filter(price__exact=Money(0, "USD")).get()
    assert ent.price == Money(0, "USD")


@pytest.mark.django_db
def test_unsupported_lookup() -> None:
    with pytest.raises(NotSupportedLookup):
        kwargs = {"price__startswith": "ABC"}
        SimpleMoneyModel.objects.filter(**kwargs)


@pytest.mark.django_db
def test_currency_accessor() -> None:
    # In the old code, accessing `instance.money_currency` would work.
    # Here we test for that and emulate the old behavior. This should
    # probably not be part of the official API and when removed, this test
    # can be removed as well.

    created = SimpleMoneyModel.objects.create(name="zero dollars", price=Money(0))
    assert created.price_currency == "XXX"
    assert created.price.currency == "XXX"

    created = SimpleMoneyModel.objects.create(
        name="zero dollars", price=Money(0, "USD")
    )
    assert created.price_currency == "USD"
    assert created.price.currency == "USD"

    # This actually wouldn't work in the old code without a round trip to the db
    created.price_currency = "EUR"
    assert created.price_currency == "EUR"
    assert created.price.currency == "EUR"

    created.save()
    created = SimpleMoneyModel.objects.get(pk=created.pk)
    assert created.price_currency == "EUR"
    assert created.price.currency == "EUR"


@pytest.mark.django_db
class TestMoneyFieldFixtureLoading(TestCase):
    """
    Rests to check that loading via fixtures works
    """

    fixtures = ["testdata.json"]

    def test_data_was_loaded(self) -> None:
        model1 = SimpleMoneyModel.objects.get(pk=1001)
        assert model1.price == Money("123.45", "USD")
        model2 = SimpleMoneyModel.objects.get(pk=1002)
        assert model2.price == Money("12345", "JPY")
