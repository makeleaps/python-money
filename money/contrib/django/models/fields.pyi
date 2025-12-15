from typing import Any

from django.db import models

from money.money import Money, Currency
from django.utils.functional import _StrOrPromise


def currency_field_name(name: str) -> str: ...


class NotSupportedLookup(TypeError): ...


class CurrencyField(models.DecimalField[str, str]): ...


class MoneyField(models.DecimalField[Money, Money]):
    _pyi_private_set_type: Money | int  # type: ignore[assignment]
    _pyi_private_get_type: Money  # type: ignore[assignment]
    _pyi_lookup_exact_type: Money | int  # type: ignore[assignment]

    max_digits: int
    decimal_places: int

    default_currency: str | Currency
    no_currency_field: bool

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
