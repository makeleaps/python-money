import pytest
from django.db import IntegrityError
from django.db.models import QuerySet
from django.test import TestCase

from money.contrib.django.models.fields import NotSupportedLookup
from money.money import CURRENCY, Money
from money.tests.models import (
    MoneyModelDefaultMoneyUSD,
    MoneyModelDefaults,
    MoneyModelWithCustomManager,
    NullableMoneyModel,
    SimpleMoneyModel,
)


@pytest.mark.django_db
class MoneyFieldTestCase(TestCase):
    def test_non_null(self) -> None:
        instance = SimpleMoneyModel()
        with pytest.raises(IntegrityError):
            instance.save()

    def test_creating(self) -> None:
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

    def test_price_from_string(self) -> None:
        price1 = Money("400", "USD")
        price2 = Money.from_string("USD 400")
        assert price1 == price2
        assert price1.amount == price2.amount
        assert price1.currency == price2.currency

    def test_retrieve(self) -> None:
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

    def test_assign(self) -> None:
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

    def test_retrieve_and_update(self) -> None:
        created = SimpleMoneyModel.objects.create(
            name="USD100", price=Money(100, "USD")
        )
        assert created.price == Money(100, "USD")

        ent = SimpleMoneyModel.objects.filter(price__exact=Money(100, "USD")).get()
        assert ent.price == Money(100, "USD")

        ent.price = Money(300, "USD")
        ent.save()

        ent = SimpleMoneyModel.objects.filter(price__exact=Money(300, "USD")).get()
        assert ent.price == Money(300, "USD")

    def test_defaults_as_money_objects(self) -> None:
        ent = MoneyModelDefaultMoneyUSD.objects.create(name="123.45 USD")
        assert ent.price == Money("123.45", "USD")

        ent = MoneyModelDefaultMoneyUSD.objects.get(pk=ent.id)
        assert ent.price == Money("123.45", "USD")

    def test_defaults_as_separate_values(self) -> None:
        ent = MoneyModelDefaults.objects.create(name="100 USD", price=100)
        assert ent.price == Money(100, "USD")

        ent = MoneyModelDefaults.objects.get(pk=ent.id)
        assert ent.price == Money(100, "USD")

    def test_lookup_with_money(self) -> None:
        USD100 = Money(100, "USD")
        EUR100 = Money(100, "EUR")
        UAH100 = Money(100, "UAH")

        SimpleMoneyModel.objects.create(name="USD100", price=USD100)
        SimpleMoneyModel.objects.create(name="USD101", price=USD100 + 1)
        SimpleMoneyModel.objects.create(name="USD99", price=USD100 - 1)

        SimpleMoneyModel.objects.create(name="EUR100", price=EUR100)
        SimpleMoneyModel.objects.create(name="EUR101", price=EUR100 + 1)
        SimpleMoneyModel.objects.create(name="EUR99", price=EUR100 - 1)

        SimpleMoneyModel.objects.create(name="UAH100", price=UAH100)
        SimpleMoneyModel.objects.create(name="UAH101", price=UAH100 + 1)
        SimpleMoneyModel.objects.create(name="UAH99", price=UAH100 - 1)

        def get_names(_queryset: QuerySet[SimpleMoneyModel]) -> tuple[str, ...]:
            return tuple(_queryset.order_by("pk").values_list("name", flat=True))

        # Exact:
        queryset = SimpleMoneyModel.objects.filter(price__exact=USD100)
        assert get_names(queryset) == ("USD100",)
        queryset = SimpleMoneyModel.objects.filter(price__exact=EUR100)
        assert get_names(queryset) == ("EUR100",)
        queryset = SimpleMoneyModel.objects.filter(price__exact=UAH100)
        assert get_names(queryset) == ("UAH100",)

        # Directt equal:
        queryset = SimpleMoneyModel.objects.filter(price=USD100)
        assert get_names(queryset) == ("USD100",)
        queryset = SimpleMoneyModel.objects.filter(price=EUR100)
        assert get_names(queryset) == ("EUR100",)
        queryset = SimpleMoneyModel.objects.filter(price=UAH100)
        assert get_names(queryset) == ("UAH100",)

        # Less than:
        queryset = SimpleMoneyModel.objects.filter(price__lt=USD100)
        assert get_names(queryset) == ("USD99",)
        queryset = SimpleMoneyModel.objects.filter(price__lt=EUR100)
        assert get_names(queryset) == ("EUR99",)
        queryset = SimpleMoneyModel.objects.filter(price__lt=UAH100)
        assert get_names(queryset) == ("UAH99",)

        # Greater than:
        queryset = SimpleMoneyModel.objects.filter(price__gt=USD100)
        assert get_names(queryset) == ("USD101",)
        queryset = SimpleMoneyModel.objects.filter(price__gt=EUR100)
        assert get_names(queryset) == ("EUR101",)
        queryset = SimpleMoneyModel.objects.filter(price__gt=UAH100)
        assert get_names(queryset) == ("UAH101",)

        # Less than or equal:
        queryset = SimpleMoneyModel.objects.filter(price__lte=USD100)
        assert get_names(queryset) == ("USD100", "USD99")
        queryset = SimpleMoneyModel.objects.filter(price__lte=EUR100)
        assert get_names(queryset) == ("EUR100", "EUR99")
        queryset = SimpleMoneyModel.objects.filter(price__lte=UAH100)
        assert get_names(queryset) == ("UAH100", "UAH99")

        # Greater than or equal:
        queryset = SimpleMoneyModel.objects.filter(price__gte=USD100)
        assert get_names(queryset) == ("USD100", "USD101")
        queryset = SimpleMoneyModel.objects.filter(price__gte=EUR100)
        assert get_names(queryset) == ("EUR100", "EUR101")
        queryset = SimpleMoneyModel.objects.filter(price__gte=UAH100)
        assert get_names(queryset) == ("UAH100", "UAH101")

    def test_lookup_with_custom_manager(self) -> None:
        USD100 = Money(100, "USD")
        EUR100 = Money(100, "EUR")
        UAH100 = Money(100, "UAH")

        MoneyModelWithCustomManager.objects.create(name="USD100", price=USD100)
        MoneyModelWithCustomManager.objects.create(name="USD101", price=USD100 + 1)
        MoneyModelWithCustomManager.objects.create(name="USD99", price=USD100 - 1)

        MoneyModelWithCustomManager.objects.create(name="EUR100", price=EUR100)
        MoneyModelWithCustomManager.objects.create(name="EUR101", price=EUR100 + 1)
        MoneyModelWithCustomManager.objects.create(name="EUR99", price=EUR100 - 1)

        MoneyModelWithCustomManager.objects.create(name="UAH100", price=UAH100)
        MoneyModelWithCustomManager.objects.create(name="UAH101", price=UAH100 + 1)
        MoneyModelWithCustomManager.objects.create(name="UAH99", price=UAH100 - 1)

        def get_names(
            _queryset: QuerySet[MoneyModelWithCustomManager],
        ) -> tuple[str, ...]:
            return tuple(_queryset.order_by("pk").values_list("name", flat=True))

        # Exact:
        queryset = MoneyModelWithCustomManager.objects.filter(price__exact=USD100)
        assert get_names(queryset) == ("USD100",)
        queryset = MoneyModelWithCustomManager.objects.filter(price__exact=EUR100)
        assert get_names(queryset) == ("EUR100",)
        queryset = MoneyModelWithCustomManager.objects.filter(price__exact=UAH100)
        assert get_names(queryset) == ("UAH100",)

        # Direct equal:
        queryset = MoneyModelWithCustomManager.objects.filter(price=USD100)
        assert get_names(queryset) == ("USD100",)
        queryset = MoneyModelWithCustomManager.objects.filter(price=EUR100)
        assert get_names(queryset) == ("EUR100",)
        queryset = MoneyModelWithCustomManager.objects.filter(price=UAH100)
        assert get_names(queryset) == ("UAH100",)

        # Less than:
        queryset = MoneyModelWithCustomManager.objects.filter(price__lt=USD100)
        assert get_names(queryset) == ("USD99",)
        queryset = MoneyModelWithCustomManager.objects.filter(price__lt=EUR100)
        assert get_names(queryset) == ("EUR99",)
        queryset = MoneyModelWithCustomManager.objects.filter(price__lt=UAH100)
        assert get_names(queryset) == ("UAH99",)

        # Greater than:
        queryset = MoneyModelWithCustomManager.objects.filter(price__gt=USD100)
        assert get_names(queryset) == ("USD101",)
        queryset = MoneyModelWithCustomManager.objects.filter(price__gt=EUR100)
        assert get_names(queryset) == ("EUR101",)
        queryset = MoneyModelWithCustomManager.objects.filter(price__gt=UAH100)
        assert get_names(queryset) == ("UAH101",)

        # Less than or equal:
        queryset = MoneyModelWithCustomManager.objects.filter(price__lte=USD100)
        assert get_names(queryset) == ("USD100", "USD99")
        queryset = MoneyModelWithCustomManager.objects.filter(price__lte=EUR100)
        assert get_names(queryset) == ("EUR100", "EUR99")
        queryset = MoneyModelWithCustomManager.objects.filter(price__lte=UAH100)
        assert get_names(queryset) == ("UAH100", "UAH99")

        # Greater than or equal:
        queryset = MoneyModelWithCustomManager.objects.filter(price__gte=USD100)
        assert get_names(queryset) == ("USD100", "USD101")
        queryset = MoneyModelWithCustomManager.objects.filter(price__gte=EUR100)
        assert get_names(queryset) == ("EUR100", "EUR101")
        queryset = MoneyModelWithCustomManager.objects.filter(price__gte=UAH100)
        assert get_names(queryset) == ("UAH100", "UAH101")

        # Custom Manager:
        queryset = MoneyModelWithCustomManager.objects.only_usd()
        assert get_names(queryset) == ("USD100", "USD101", "USD99")
        queryset = MoneyModelWithCustomManager.objects.only_usd(price__lte=USD100)
        assert get_names(queryset) == ("USD100", "USD99")
        queryset = MoneyModelWithCustomManager.objects.only_usd(price__lte=EUR100)
        assert get_names(queryset) == tuple()

    def test_price_attribute(self) -> None:
        e = SimpleMoneyModel()
        e.price = Money(3, "BGN")
        assert e.price == Money(3, "BGN")

        e.price = Money.from_string("BGN 5.0")
        assert e.price == Money(5, "BGN")

    def test_price_attribute_in_constructor(self) -> None:
        e1 = SimpleMoneyModel(price=Money(100, "USD"))
        e2 = SimpleMoneyModel(price=Money(200, "JPY"))
        assert e1.price == Money(100, "USD")
        assert e2.price == Money(200, "JPY")

    def test_price_attribute_update(self) -> None:
        e2 = SimpleMoneyModel(price=Money(200, "JPY"))
        e2.price = Money(300, "USD")
        assert e2.price == Money(300, "USD")

    def test_price_amount_to_string(self) -> None:
        e1 = SimpleMoneyModel(price=Money("200", "JPY"))
        e2 = SimpleMoneyModel(price=Money("200.0", "JPY"))

        assert str(e1.price) == "JPY 200"

        assert str(e1.price.amount) == "200"

        assert str(e2.price.amount) == "200.0"

    def test_price_amount_to_string_non_money(self) -> None:
        e1 = MoneyModelDefaults()

        assert str(e1.price) == "USD 123.45"

        assert str(e1.price.amount) == "123.45"

    def test_zero_edge_case(self) -> None:
        created = SimpleMoneyModel.objects.create(
            name="zero dollars", price=Money(0, "USD")
        )
        assert created.price == Money(0, "USD")

        ent = SimpleMoneyModel.objects.filter(price__exact=Money(0, "USD")).get()
        assert ent.price == Money(0, "USD")

    def test_unsupported_lookup(self) -> None:
        with pytest.raises(NotSupportedLookup):
            kwargs = {"price__startswith": "ABC"}
            SimpleMoneyModel.objects.filter(**kwargs)

    def test_currency_accessor(self) -> None:
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
class TestNullability(TestCase):
    def test_nullable_model_instance(self) -> None:
        instance = NullableMoneyModel()
        assert instance.price is None

    def test_nullable_model_save(self) -> None:
        instance = NullableMoneyModel()
        instance.save()
        assert instance.price is None

    def test_nullable_model_create_and_lookup(self) -> None:
        name = "test_nullable_model_create_and_lookup"
        NullableMoneyModel.objects.create(name=name)
        instance = NullableMoneyModel.objects.get(name=name)
        assert instance.price is None

    def test_nullable_model_lookup_by_null_amount(self) -> None:
        name = "test_nullable_model_lookup_by_null_amount"
        NullableMoneyModel.objects.create(name=name)

        # Assert NULL currency has "blank" currency
        instance = NullableMoneyModel.objects.filter(price_currency="")[0]
        assert instance.name == name

    def test_nullable_model_lookup_by_null_currency(self) -> None:
        name = "test_nullable_model_lookup_by_null_currency"
        NullableMoneyModel.objects.create(name=name)

        # Assert NULL currency has "blank" currency
        instance = NullableMoneyModel.objects.filter(price__isnull=True)[0]
        assert instance.name == name

    def test_nullable_null_currency_vs_undefined_currency(self) -> None:
        name = "test_nullable_null_currency_vs_undefined_currency"
        NullableMoneyModel.objects.create(name=name + "_null", price=None)
        NullableMoneyModel.objects.create(name=name + "_undefined", price=Money(0))
        assert NullableMoneyModel.objects.all().count() == 2

        # Assert NULL currency has "blank" currency
        assert NullableMoneyModel.objects.filter(price__isnull=True).count() == 1

        null_instance = NullableMoneyModel.objects.filter(price__isnull=True)[0]
        assert null_instance.name == name + "_null"
        null_instance = NullableMoneyModel.objects.filter(price_currency="")[0]
        assert null_instance.name == name + "_null"

        assert NullableMoneyModel.objects.filter(price__isnull=False).count() == 1
        undefined_instance = NullableMoneyModel.objects.filter(price__isnull=False)[0]
        assert undefined_instance.name == name + "_undefined"
        undefined_instance = NullableMoneyModel.objects.filter(price_currency="XXX")[0]
        assert undefined_instance.name == name + "_undefined"


@pytest.mark.django_db
class TestMoneyFieldFixtureLoading(TestCase):
    """
    Rests to check that loading via fixtures works
    """

    fixtures = [
        "testdata.json",
    ]

    def test_data_was_loaded(self) -> None:
        model1 = SimpleMoneyModel.objects.get(pk=1001)
        assert model1.price == Money("123.45", "USD")
        model2 = SimpleMoneyModel.objects.get(pk=1002)
        assert model2.price == Money("12345", "JPY")
