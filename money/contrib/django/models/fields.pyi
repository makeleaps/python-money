from decimal import Decimal
from typing import Any, TypeVar

from django.db import models
from django.db.models import Combinable
from django.utils.functional import _StrOrPromise

from money.money import Currency, Money

class NotSupportedLookup(TypeError): ...

class CurrencyField(models.CharField[str, str]):
    _pyi_private_set_type: str | int | Combinable | Currency  # type: ignore[assignment]
    _pyi_private_get_type: str

F = TypeVar("F", bound="MoneyField")

class MoneyField(models.DecimalField[Money, Money]):
    _pyi_private_set_type: Money | Decimal | int  # type: ignore[assignment]
    _pyi_private_get_type: Money  # type: ignore[assignment]
    _pyi_lookup_exact_type: Money | Decimal | int  # type: ignore[assignment]

    currency_field_name: str

    max_digits: int
    decimal_places: int

    default_currency: str | Currency
    add_currency_field: bool

    def __init__(
        self,
        verbose_name: _StrOrPromise | None = ...,
        name: str | None = ...,
        max_digits: int | None = ...,
        decimal_places: int | None = ...,
        *,
        primary_key: bool = ...,
        unique: bool = ...,
        blank: bool = ...,
        null: bool = ...,
        db_index: bool = ...,
        default: Any = ...,
        editable: bool = ...,
        auto_created: bool = ...,
        serialize: bool = ...,
        help_text: _StrOrPromise = ...,
        db_column: str | None = ...,
        db_tablespace: str | None = ...,
        # new in MoneyField, not in Django fields
        default_currency: str | Currency = ...,
        no_currency_field: bool = ...,
    ) -> None: ...
