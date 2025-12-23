import pytest
from django.db.models import Model, QuerySet

from money.money import Money
from money.tests.models import MoneyModelWithCustomManager, SimpleMoneyModel

USD100 = Money(100, "USD")
EUR100 = Money(100, "EUR")
UAH100 = Money(100, "UAH")


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

    SimpleMoneyModel.objects.create(name="UAH100", price=UAH100)
    SimpleMoneyModel.objects.create(name="UAH101", price=UAH100 + 1)
    SimpleMoneyModel.objects.create(name="UAH99", price=UAH100 - 1)

    # Exact:
    queryset = SimpleMoneyModel.objects.filter(price__exact=USD100)
    assert get_names(queryset) == ("USD100",)
    queryset = SimpleMoneyModel.objects.filter(price__exact=EUR100)
    assert get_names(queryset) == ("EUR100",)
    queryset = SimpleMoneyModel.objects.filter(price__exact=UAH100)
    assert get_names(queryset) == ("UAH100",)

    # Direct equal:
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


@pytest.mark.django_db
def test_lookup_with_custom_manager() -> None:
    MoneyModelWithCustomManager.objects.create(name="USD100", price=USD100)
    MoneyModelWithCustomManager.objects.create(name="USD101", price=USD100 + 1)
    MoneyModelWithCustomManager.objects.create(name="USD99", price=USD100 - 1)

    MoneyModelWithCustomManager.objects.create(name="EUR100", price=EUR100)
    MoneyModelWithCustomManager.objects.create(name="EUR101", price=EUR100 + 1)
    MoneyModelWithCustomManager.objects.create(name="EUR99", price=EUR100 - 1)

    MoneyModelWithCustomManager.objects.create(name="UAH100", price=UAH100)
    MoneyModelWithCustomManager.objects.create(name="UAH101", price=UAH100 + 1)
    MoneyModelWithCustomManager.objects.create(name="UAH99", price=UAH100 - 1)

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
