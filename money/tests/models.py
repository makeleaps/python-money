from __future__ import unicode_literals


from django.db import models

from money.contrib.django.models import fields
from money.money import Money


# Tests for Django models. We set up three types of models with different
# ways of specifying defaults
class SimpleMoneyModel(models.Model):
    name = models.CharField(max_length=100)

    price = fields.MoneyField(max_digits=12, decimal_places=3)
    price_currency: fields.CurrencyField

    def __str__(self):
        return self.name + " " + str(self.price)

    class Meta:
        app_label = "tests"


class MoneyModelDefaultMoneyUSD(models.Model):
    name = models.CharField(max_length=100)
    price = fields.MoneyField(
        max_digits=12, decimal_places=3, default=Money("123.45", "USD")
    )
    price_currency: fields.CurrencyField

    zero = fields.MoneyField(max_digits=12, decimal_places=3, default=Money("0", "USD"))
    zero_currency: fields.CurrencyField

    def __str__(self):
        return self.name + " " + str(self.price)

    class Meta:
        app_label = "tests"


class MoneyModelDefaults(models.Model):
    name = models.CharField("Name", max_length=100)
    price = fields.MoneyField(
        "Price",
        max_digits=12,
        decimal_places=3,
        default="123.45",
        default_currency="USD",
    )
    price_currency: fields.CurrencyField

    zero = fields.MoneyField(
        "Zero", max_digits=12, decimal_places=3, default="0", default_currency="USD"
    )
    zero_currency: fields.CurrencyField

    def __str__(self):
        return self.name + " " + str(self.price)

    class Meta:
        app_label = "tests"


class NullableMoneyModel(models.Model):
    name = models.CharField(max_length=100)

    price = fields.MoneyField(max_digits=12, decimal_places=3, null=True)
    price_currency: fields.CurrencyField

    def __str__(self):
        return self.name + " " + str(self.price)

    class Meta:
        app_label = "tests"


# A parametrized way of testing the model defaults. The following are all
# acceptable ways the field can be defined on a model
class ParametrizedModel(models.Model):
    """The simplest possible declaration"""

    value = fields.MoneyField(max_digits=12, decimal_places=3, default=123)
    value_currency: fields.CurrencyField

    def expected_value(self):
        return Money("123", "XXX")


class ParametrizedDefaultAsZeroMoneyModel(models.Model):
    """The simplest possible declaration with a Money object"""

    value = fields.MoneyField(max_digits=12, decimal_places=3, default=Money(0, "JPY"))
    value_currency: fields.CurrencyField

    def expected_value(self):
        return Money("0", "JPY")


class ParametrizedDefaultAsMoneyModel(models.Model):
    """The simplest possible declaration with a Money object"""

    value = fields.MoneyField(
        max_digits=12, decimal_places=3, default=Money(100, "JPY")
    )
    value_currency: fields.CurrencyField

    def expected_value(self):
        return Money("100", "JPY")


class ParametrizedDefaultAsZeroModel(models.Model):
    """The simplest possible declaration with a zero default"""

    value = fields.MoneyField(max_digits=12, decimal_places=3, default=0)
    value_currency: fields.CurrencyField

    def expected_value(self):
        return Money("0", "XXX")


class ParametrizedDefaultAsValueModel(models.Model):
    """The simplest possible declaration with a non-zero default"""

    value = fields.MoneyField(max_digits=12, decimal_places=3, default=100)
    value_currency: fields.CurrencyField

    def expected_value(self):
        return Money("100", "XXX")


class ParametrizedDefaultAsValueWithCurrencyModel(models.Model):
    """The simplest possible declaration with a zero default"""

    value = fields.MoneyField(
        max_digits=12, decimal_places=3, default=0, default_currency="JPY"
    )
    value_currency: fields.CurrencyField

    def expected_value(self):
        return Money("0", "JPY")


class ParametrizedDefaultAsValueWithCurrencyAndLabelModel(models.Model):
    """The simplest possible declaration with a zero default and a label"""

    value = fields.MoneyField(
        "Value", max_digits=12, decimal_places=3, default=0, default_currency="JPY"
    )
    value_currency: fields.CurrencyField

    def expected_value(self):
        return Money("0", "JPY")


ALL_PARAMETRIZED_MODELS = [
    ParametrizedModel,
    ParametrizedDefaultAsZeroMoneyModel,
    ParametrizedDefaultAsMoneyModel,
    ParametrizedDefaultAsZeroModel,
    ParametrizedDefaultAsValueModel,
    ParametrizedDefaultAsValueWithCurrencyModel,
    ParametrizedDefaultAsValueWithCurrencyAndLabelModel,
]
