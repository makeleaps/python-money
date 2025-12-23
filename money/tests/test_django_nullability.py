import pytest

from money import Money
from money.tests.models import NullableMoneyModel


@pytest.mark.django_db
def test_nullable_model_instance() -> None:
    instance = NullableMoneyModel()
    assert instance.price is None


@pytest.mark.django_db
def test_nullable_model_save() -> None:
    instance = NullableMoneyModel()
    instance.save()
    assert instance.price is None


@pytest.mark.django_db
def test_nullable_model_create_and_lookup() -> None:
    name = "test_nullable_model_create_and_lookup"
    NullableMoneyModel.objects.create(name=name)
    instance = NullableMoneyModel.objects.get(name=name)
    assert instance.price is None


@pytest.mark.django_db
def test_nullable_model_lookup_by_null_amount() -> None:
    name = "test_nullable_model_lookup_by_null_amount"
    NullableMoneyModel.objects.create(name=name)

    # Assert NULL currency has "blank" currency
    instance = NullableMoneyModel.objects.filter(price_currency="")[0]
    assert instance.name == name


@pytest.mark.django_db
def test_nullable_model_lookup_by_null_currency() -> None:
    name = "test_nullable_model_lookup_by_null_currency"
    NullableMoneyModel.objects.create(name=name)

    # Assert NULL currency has "blank" currency
    instance = NullableMoneyModel.objects.filter(price__isnull=True)[0]
    assert instance.name == name


@pytest.mark.django_db
def test_nullable_null_currency_vs_undefined_currency() -> None:
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
