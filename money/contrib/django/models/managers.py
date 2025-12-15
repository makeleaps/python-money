from typing import Any, TypeVar

from django.db import models
from django.db.models.query import QuerySet
from django.utils.encoding import smart_str
from .fields import currency_field_name

__all__ = (
    "QuerysetWithMoney",
    "MoneyManager",
)

T = TypeVar("T", bound=models.Model)


class QuerysetWithMoney(QuerySet[T]):
    def _update_params(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        from django.db.models.constants import LOOKUP_SEP
        from money.money import Money

        to_append = {}
        for name, value in kwargs.items():
            if isinstance(value, Money):
                path = name.split(LOOKUP_SEP)
                if len(path) > 1:
                    field_name = currency_field_name(path[0])
                else:
                    field_name = currency_field_name(name)
                to_append[field_name] = smart_str(value.currency)
        kwargs.update(to_append)
        return kwargs

    def dates(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().dates(*args, **kwargs)

    def distinct(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().distinct(*args, **kwargs)

    def extra(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().extra(*args, **kwargs)

    def get(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().get(*args, **kwargs)

    def get_or_create(self, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().get_or_create(**kwargs)

    def filter(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().filter(*args, **kwargs)

    def complex_filter(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().complex_filter(*args, **kwargs)

    def exclude(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().exclude(*args, **kwargs)

    def in_bulk(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().in_bulk(*args, **kwargs)

    def iterator(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().iterator(*args, **kwargs)

    def latest(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().latest(*args, **kwargs)

    def order_by(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().order_by(*args, **kwargs)

    def select_related(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().select_related(*args, **kwargs)

    def values(self, *args, **kwargs):
        kwargs = self._update_params(kwargs)
        return super().values(*args, **kwargs)


class MoneyManager(models.Manager[T]):
    def get_queryset(self):
        return QuerysetWithMoney(self.model)
