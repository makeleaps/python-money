from __future__ import unicode_literals

from typing import Iterable, Optional

import pytest

from django.test import TestCase
from django.db import IntegrityError
from money.money import Money, CURRENCY
from money.contrib.django.models.fields import NotSupportedLookup
from money.tests.models import (
    SimpleMoneyModel,
    MoneyModelDefaultMoneyUSD,
    MoneyModelDefaults,
    NullableMoneyModel,
)


@pytest.mark.django_db
class MoneyFieldTestCase(TestCase):
    def assertSameCurrency(
        self, moneys: Iterable[Money], currency_code: Optional[str] = None
    ) -> None:
        """Utility function to assert a collection of currencies are all the same"""
        currency_codes = set([m.currency.code for m in moneys])
        self.assertTrue(len(currency_codes) == 1)
        if currency_code:
            self.assertEqual(currency_codes.pop(), currency_code)

    def test_non_null(self):
        instance = SimpleMoneyModel()
        with pytest.raises(IntegrityError):
            instance.save()

    def test_creating(self):
        ind = 0
        for code, currency in CURRENCY.items():
            ind = ind + 1
            price = Money(ind * 1000.0, code)
            SimpleMoneyModel.objects.create(
                name=currency.name, price=price.amount, price_currency=price.currency
            )
        count = SimpleMoneyModel.objects.all().count()
        self.assertEqual(len(CURRENCY), count)

        for code in CURRENCY:
            count = SimpleMoneyModel.objects.filter(price_currency=code).count()
            self.assertTrue(count == 1)

    def test_price_from_string(self):
        price1 = Money("400", "USD")
        price2 = Money.from_string("USD 400")
        self.assertEqual(price1, price2)
        self.assertEqual(price1.amount, price2.amount)
        self.assertEqual(price1.currency, price2.currency)

    def test_retrieve(self):
        price = Money(100, "USD")
        SimpleMoneyModel.objects.create(name="one hundred dollars", price=price)

        # Filter
        queryset = SimpleMoneyModel.objects.filter(price=price)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset[0].price, price)

        # Get
        entry = SimpleMoneyModel.objects.get(price=price)
        self.assertEqual(entry.price, price)

        # test retrieving without currency
        entry = SimpleMoneyModel.objects.get(price=100)
        self.assertEqual(entry.price, price)

    def test_assign(self):
        price = Money(100, "USD")
        ent = SimpleMoneyModel(
            name="test", price=price.amount, price_currency=price.currency
        )
        ent.save()
        self.assertEqual(ent.price, Money(100, "USD"))

        ent.price = Money(10, "USD")
        ent.save()
        self.assertEqual(ent.price, Money(10, "USD"))

        ent_same = SimpleMoneyModel.objects.get(pk=ent.id)
        self.assertEqual(ent_same.price, Money(10, "USD"))

    def test_retrieve_and_update(self):
        created = SimpleMoneyModel.objects.create(
            name="one hundred dollars", price=Money(100, "USD")
        )
        created.save()
        self.assertEqual(created.price, Money(100, "USD"))

        ent = SimpleMoneyModel.objects.filter(price__exact=Money(100, "USD")).get()
        self.assertEqual(ent.price, Money(100, "USD"))

        ent.price = Money(300, "USD")
        ent.save()

        ent = SimpleMoneyModel.objects.filter(price__exact=Money(300, "USD")).get()
        self.assertEqual(ent.price, Money(300, "USD"))

    def test_defaults_as_money_objects(self):
        ent = MoneyModelDefaultMoneyUSD.objects.create(name="123.45 USD")
        self.assertEqual(ent.price, Money("123.45", "USD"))

        ent = MoneyModelDefaultMoneyUSD.objects.get(pk=ent.id)
        self.assertEqual(ent.price, Money("123.45", "USD"))

    def test_defaults_as_separate_values(self):
        ent = MoneyModelDefaults.objects.create(name="100 USD", price=100)
        self.assertEqual(ent.price, Money(100, "USD"))

        ent = MoneyModelDefaults.objects.get(pk=ent.id)
        self.assertEqual(ent.price, Money(100, "USD"))

    def test_lookup(self):
        USD100 = Money(100, "USD")
        EUR100 = Money(100, "EUR")
        UAH100 = Money(100, "UAH")

        SimpleMoneyModel.objects.create(name="one hundred dollars", price=USD100)
        SimpleMoneyModel.objects.create(
            name="one hundred and one dollars", price=USD100 + 1
        )
        SimpleMoneyModel.objects.create(name="ninety nine dollars", price=USD100 - 1)

        SimpleMoneyModel.objects.create(name="one hundred euros", price=EUR100)
        SimpleMoneyModel.objects.create(
            name="one hundred and one euros", price=EUR100 + 1
        )
        SimpleMoneyModel.objects.create(name="ninety nine euros", price=EUR100 - 1)

        SimpleMoneyModel.objects.create(name="one hundred hryvnias", price=UAH100)
        SimpleMoneyModel.objects.create(
            name="one hundred and one hryvnias", price=UAH100 + 1
        )
        SimpleMoneyModel.objects.create(name="ninety nine hryvnias", price=UAH100 - 1)

        # Exact:
        queryset = SimpleMoneyModel.objects.filter(price__exact=USD100)
        self.assertEqual(queryset.count(), 1)
        queryset = SimpleMoneyModel.objects.filter(price__exact=EUR100)
        self.assertEqual(queryset.count(), 1)
        queryset = SimpleMoneyModel.objects.filter(price__exact=UAH100)
        self.assertEqual(queryset.count(), 1)

        # Less than:
        queryset = SimpleMoneyModel.objects.filter(price__lt=USD100)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset[0].price, USD100 - 1)

        queryset = SimpleMoneyModel.objects.filter(price__lt=EUR100)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset[0].price, EUR100 - 1)

        queryset = SimpleMoneyModel.objects.filter(price__lt=UAH100)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset[0].price, UAH100 - 1)

        # Greater than:
        queryset = SimpleMoneyModel.objects.filter(price__gt=USD100)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset[0].price, USD100 + 1)

        queryset = SimpleMoneyModel.objects.filter(price__gt=EUR100)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset[0].price, EUR100 + 1)

        queryset = SimpleMoneyModel.objects.filter(price__gt=UAH100)
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset[0].price, UAH100 + 1)

        # Less than or equal:
        queryset = SimpleMoneyModel.objects.filter(price__lte=USD100)
        self.assertEqual(queryset.count(), 2)
        self.assertSameCurrency([ent.price for ent in queryset], "USD")
        for ent in queryset:
            self.assertTrue(ent.price.amount <= 100)

        queryset = SimpleMoneyModel.objects.filter(price__lte=EUR100)
        self.assertEqual(queryset.count(), 2)
        self.assertSameCurrency([ent.price for ent in queryset], "EUR")
        for ent in queryset:
            self.assertTrue(ent.price.amount <= 100)

        queryset = SimpleMoneyModel.objects.filter(price__lte=UAH100)
        self.assertEqual(queryset.count(), 2)
        self.assertSameCurrency([ent.price for ent in queryset], "UAH")
        for ent in queryset:
            self.assertTrue(ent.price.amount <= 100)

        # Greater than or equal:
        queryset = SimpleMoneyModel.objects.filter(price__gte=USD100)
        self.assertEqual(queryset.count(), 2)
        self.assertSameCurrency([ent.price for ent in queryset], "USD")

        queryset = SimpleMoneyModel.objects.filter(price__gte=EUR100)
        self.assertEqual(queryset.count(), 2)
        self.assertSameCurrency([ent.price for ent in queryset], "EUR")

        queryset = SimpleMoneyModel.objects.filter(price__gte=UAH100)
        self.assertEqual(queryset.count(), 2)
        self.assertSameCurrency([ent.price for ent in queryset], "UAH")

    def test_price_attribute(self):
        e = SimpleMoneyModel()
        e.price = Money(3, "BGN")
        self.assertEqual(e.price, Money(3, "BGN"))

        e.price = Money.from_string("BGN 5.0")
        self.assertEqual(e.price, Money(5, "BGN"))

    def test_price_attribute_in_constructor(self):
        e1 = SimpleMoneyModel(price=Money(100, "USD"))
        e2 = SimpleMoneyModel(price=Money(200, "JPY"))
        self.assertEqual(e1.price, Money(100, "USD"))
        self.assertEqual(e2.price, Money(200, "JPY"))

    def test_price_attribute_update(self):
        e2 = SimpleMoneyModel(price=Money(200, "JPY"))
        e2.price = Money(300, "USD")
        self.assertEqual(e2.price, Money(300, "USD"))

    def test_price_amount_to_string(self):
        e1 = SimpleMoneyModel(price=Money("200", "JPY"))
        e2 = SimpleMoneyModel(price=Money("200.0", "JPY"))

        self.assertEqual(str(e1.price), "JPY 200")

        self.assertEqual(str(e1.price.amount), "200")

        self.assertEqual(str(e2.price.amount), "200.0")

    def test_price_amount_to_string_non_money(self):
        e1 = MoneyModelDefaults()

        self.assertEqual(str(e1.price), "USD 123.45")

        self.assertEqual(str(e1.price.amount), "123.45")

    def test_zero_edge_case(self):
        created = SimpleMoneyModel.objects.create(
            name="zero dollars", price=Money(0, "USD")
        )
        self.assertEqual(created.price, Money(0, "USD"))

        ent = SimpleMoneyModel.objects.filter(price__exact=Money(0, "USD")).get()
        self.assertEqual(ent.price, Money(0, "USD"))

    def test_unsupported_lookup(self):
        with pytest.raises(NotSupportedLookup):
            SimpleMoneyModel.objects.filter(price__startswith="ABC")

    def test_currency_accessor(self):
        # In the old code, accessing `instance.money_currency` would work.
        # Here we test for that and emulate the old behavior. This should
        # probably not be part of the official API and when removed, this test
        # can be removed as well.

        created = SimpleMoneyModel.objects.create(name="zero dollars", price=Money(0))
        self.assertEqual(created.price_currency, "XXX")
        self.assertEqual(created.price.currency, "XXX")

        created = SimpleMoneyModel.objects.create(
            name="zero dollars", price=Money(0, "USD")
        )
        self.assertEqual(created.price_currency, "USD")
        self.assertEqual(created.price.currency, "USD")

        # This actually wouldn't work in the old code without a round trip to the db
        created.price_currency = "EUR"
        self.assertEqual(created.price_currency, "EUR")
        self.assertEqual(created.price.currency, "EUR")

        created.save()
        created = SimpleMoneyModel.objects.get(pk=created.pk)
        self.assertEqual(created.price_currency, "EUR")
        self.assertEqual(created.price.currency, "EUR")


@pytest.mark.django_db
class TestNullability(TestCase):
    def test_nullable_model_instance(self):
        instance = NullableMoneyModel()
        self.assertEqual(instance.price, None)

    def test_nullable_model_save(self):
        instance = NullableMoneyModel()
        instance.save()
        self.assertEqual(instance.price, None)

    def test_nullable_model_create_and_lookup(self):
        name = "test_nullable_model_create_and_lookup"
        NullableMoneyModel.objects.create(name=name)
        instance = NullableMoneyModel.objects.get(name=name)
        self.assertEqual(instance.price, None)

    def test_nullable_model_lookup_by_null_amount(self):
        name = "test_nullable_model_lookup_by_null_amount"
        NullableMoneyModel.objects.create(name=name)

        # Assert NULL currency has "blank" currency
        instance = NullableMoneyModel.objects.filter(price_currency="")[0]
        self.assertEqual(instance.name, name)

    def test_nullable_model_lookup_by_null_currency(self):
        name = "test_nullable_model_lookup_by_null_currency"
        NullableMoneyModel.objects.create(name=name)

        # Assert NULL currency has "blank" currency
        instance = NullableMoneyModel.objects.filter(price__isnull=True)[0]
        self.assertEqual(instance.name, name)

    def test_nullable_null_currency_vs_undefined_currency(self):
        name = "test_nullable_null_currency_vs_undefined_currency"
        NullableMoneyModel.objects.create(name=name + "_null", price=None)
        NullableMoneyModel.objects.create(name=name + "_undefined", price=Money(0))
        self.assertEqual(NullableMoneyModel.objects.all().count(), 2)

        # Assert NULL currency has "blank" currency
        self.assertEqual(
            NullableMoneyModel.objects.filter(price__isnull=True).count(), 1
        )
        null_instance = NullableMoneyModel.objects.filter(price__isnull=True)[0]
        self.assertEqual(null_instance.name, name + "_null")
        null_instance = NullableMoneyModel.objects.filter(price_currency="")[0]
        self.assertEqual(null_instance.name, name + "_null")

        self.assertEqual(
            NullableMoneyModel.objects.filter(price__isnull=False).count(), 1
        )
        undefined_instance = NullableMoneyModel.objects.filter(price__isnull=False)[0]
        self.assertEqual(undefined_instance.name, name + "_undefined")
        undefined_instance = NullableMoneyModel.objects.filter(price_currency="XXX")[0]
        self.assertEqual(undefined_instance.name, name + "_undefined")


@pytest.mark.django_db
class TestMoneyFieldFixtureLoading(TestCase):
    """
    Rests to check that loading via fixtures works
    """

    fixtures = [
        "testdata.json",
    ]

    def test_data_was_loaded(self):
        model1 = SimpleMoneyModel.objects.get(pk=1001)
        self.assertEqual(model1.price, Money("123.45", "USD"))
        model2 = SimpleMoneyModel.objects.get(pk=1002)
        self.assertEqual(model2.price, Money("12345", "JPY"))
