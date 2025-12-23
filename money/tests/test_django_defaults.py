import pytest

from money.dataclasses.money import Money
from money.tests.models import ALL_PARAMETRIZED_MODELS, ParametrizedModelType


@pytest.mark.django_db
@pytest.mark.parametrize("cls", ALL_PARAMETRIZED_MODELS)
def test_manager_create(cls: ParametrizedModelType) -> None:
    instance = cls.objects.create()

    expected_value = instance.expected_value
    assert instance.value == expected_value
    assert instance.value.amount == expected_value.amount
    assert instance.value.currency == expected_value.currency


@pytest.mark.parametrize("cls", ALL_PARAMETRIZED_MODELS)
def test_instance_create(cls: ParametrizedModelType) -> None:
    instance = cls()  # should not touch the db

    expected_value = instance.expected_value
    assert instance.value == expected_value
    assert instance.value.amount == expected_value.amount
    assert instance.value.currency == expected_value.currency


@pytest.mark.django_db
@pytest.mark.parametrize("cls", ALL_PARAMETRIZED_MODELS)
def test_instance_save(cls: ParametrizedModelType) -> None:
    instance = cls()
    instance.save()

    expected_value = instance.expected_value
    assert instance.value == expected_value
    assert instance.value.amount == expected_value.amount
    assert instance.value.currency == expected_value.currency


@pytest.mark.django_db
@pytest.mark.parametrize("cls", ALL_PARAMETRIZED_MODELS)
def test_manager_create_override_with_money(cls: ParametrizedModelType) -> None:
    overridden_value = Money("9876", "EUR")
    instance = cls.objects.create(value=overridden_value)

    expected_value = instance.expected_value
    assert instance.value != expected_value
    assert instance.value.amount != expected_value.amount
    assert instance.value.currency != expected_value.currency

    assert instance.value == overridden_value
    assert instance.value.amount == overridden_value.amount
    assert instance.value.currency == overridden_value.currency


@pytest.mark.parametrize("cls", ALL_PARAMETRIZED_MODELS)
def test_instance_create_override_with_money(cls: ParametrizedModelType) -> None:
    overridden_value = Money("8765", "EUR")
    instance = cls(value=overridden_value)

    expected_value = instance.expected_value
    assert instance.value != expected_value
    assert instance.value.amount != expected_value.amount
    assert instance.value.currency != expected_value.currency

    assert instance.value == overridden_value
    assert instance.value.amount == overridden_value.amount
    assert instance.value.currency == overridden_value.currency
