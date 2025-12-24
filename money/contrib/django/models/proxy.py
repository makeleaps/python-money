from decimal import Decimal
from typing import TYPE_CHECKING, Any

from django.db import models

from money.dataclasses.currency import Currency
from money.dataclasses.money import Money

if TYPE_CHECKING:
    from money.contrib.django.models.fields import MoneyField


class MoneyFieldProxy:
    """
    An equivalent to Django's default attribute descriptor class SubfieldBase
    (normally enabled via `__metaclass__ = models.SubfieldBase` on the custom
    Field class).

    Instead of calling to_python() on our MoneyField class as SubfieldBase
    does, it stores the two different parts separately, and updates them
    whenever something is assigned. If the attribute is read, it builds the
    instance "on-demand" with the current data.

    See: http://blog.elsdoerfer.name/2008/01/08/fuzzydates-or-one-django-model-field-multiple-database-columns/
    """

    def __init__(self, field: "MoneyField"):
        self.field = field
        self.amount_field_name: str = field.name
        self.currency_field_name: str = field.currency_field_name

    def _get_values(self, obj: models.Model) -> tuple[Decimal | None, str | None]:
        return (
            obj.__dict__.get(self.amount_field_name, None),
            obj.__dict__.get(self.currency_field_name, None),
        )

    def _set_values(
        self,
        obj: models.Model,
        amount: Decimal | None,
        currency: str | Currency | None,
    ) -> None:
        obj.__dict__[self.amount_field_name] = amount
        obj.__dict__[self.currency_field_name] = currency

    def __get__(self, obj: models.Model, *args: Any) -> Any:
        if obj is None:
            return self
        amount, currency = self._get_values(obj)
        if amount is None:
            return None
        return Money(amount, currency)

    def __set__(self, obj: models.Model, value: Any) -> Any:
        if value is None:  # Money(0) is False
            self._set_values(obj, None, "")
        elif isinstance(value, Money):
            self._set_values(obj, value.amount, value.currency.code)
        elif isinstance(value, Decimal):
            _, currency = self._get_values(obj)  # use what is currently set
            self._set_values(obj, value, currency)
        else:
            # It could be an int, or some other python native type
            try:
                amount = Decimal(str(value))
                _, currency = self._get_values(obj)  # use what is currently set
                self._set_values(obj, amount, currency)
            except TypeError:
                # Lastly, assume string type 'XXX 123' or something Money can
                # handle.
                try:
                    _, currency = self._get_values(obj)  # use what is currently set
                    m = Money.from_string(str(value))
                    self._set_values(obj, m.amount, m.currency)
                except TypeError:
                    msg = 'Cannot assign "%s"' % type(value)
                    raise TypeError(msg)
