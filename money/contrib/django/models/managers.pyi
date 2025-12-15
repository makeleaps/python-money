from typing import Any

from django.db.models import Manager
from django.db.models.query import _QuerySet, _T


class QuerysetWithMoney(_QuerySet[_T, _T]):
    def _update_params(self, kwargs: dict[str, Any]) -> dict[str, Any]: ...


class MoneyManager(Manager[_T]):
    def get_queryset(self) -> QuerysetWithMoney[_T]: ...
