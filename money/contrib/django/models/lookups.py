from typing import TYPE_CHECKING, Any, TypeVar

from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.models import Lookup
from django.db.models.expressions import Col, Expression
from django.db.models.sql.compiler import SQLCompiler
from typing_extensions import TypeAlias

from money.money import Money

T = TypeVar("T")
_ParamT: TypeAlias = str | int
_ParamsT: TypeAlias = list[_ParamT]
_AsSqlType: TypeAlias = tuple[str, _ParamsT]


class MoneyCurrencyLookupMixin:
    """
    Mixin for lookups that need to check currency when Money objects are used.

    This mixin expects to be mixed with django.db.models.Lookup and uses
    the following attributes/methods from that class:
    - process_lhs(): Process left-hand side of the lookup
    - process_rhs(): Process right-hand side of the lookup
    - lhs: Left-hand side expression (Col)
    - rhs: Right-hand side value
    - operator: SQL operator string
    """

    if TYPE_CHECKING:
        # Type stubs for attributes/methods provided by Lookup base class
        operator: str
        rhs: Any
        lhs: "Col"

        def process_lhs(
            self,
            compiler: SQLCompiler,
            connection: BaseDatabaseWrapper,
            lhs: Expression | None = ...,
        ) -> _AsSqlType: ...

        def process_rhs(
            self, compiler: SQLCompiler, connection: BaseDatabaseWrapper
        ) -> _AsSqlType: ...

    def as_sql(
        self, compiler: SQLCompiler, connection: BaseDatabaseWrapper
    ) -> _AsSqlType:
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)

        # Check if the original rhs value (before processing) is a Money object
        if isinstance(self.rhs, Money):
            from money.contrib.django.models.fields import CurrencyField, MoneyField

            # Retrieve money object
            money = self.rhs

            # SQL for amount condition
            amount_condition = f"{lhs} {self.operator} {rhs}"
            amount_condition_sql = f"({amount_condition})"
            amount_condition_params = lhs_params + [str(money.amount)]

            # Get the money field
            model = self.lhs.field.model
            money_field = model._meta.get_field(field_name=self.lhs.field.name)

            # If it is not Money Field, do a normal lookup with Money.amount
            if not isinstance(money_field, MoneyField):
                return amount_condition_sql, amount_condition_params

            # If there is no currency_field, do a normal lookup with Money.amount
            if not money_field.add_currency_field:
                return amount_condition_sql, amount_condition_params

            # Get currency field
            currency_field_name = money_field.currency_field_name
            currency_field = model._meta.get_field(field_name=currency_field_name)

            # If it is not a Currency Field, do a normal lookup with Money.amount
            if not isinstance(currency_field, CurrencyField):
                return amount_condition_sql, amount_condition_params

            currency_column = currency_field.column
            # If currency_column is None, do a normal lookup with Money.amount
            if not currency_column:
                return amount_condition_sql, amount_condition_params

            # Build SQL that checks both amount and currency
            table_name = self.lhs.alias
            currency_lhs = f"{compiler.quote_name_unless_alias(table_name)}.{compiler.quote_name_unless_alias(currency_column)}"

            # Construct the full condition
            currency_condition = f"{currency_lhs} = %s"
            sql = f"({amount_condition} AND {currency_condition})"
            params: _ParamsT = lhs_params + [
                str(self.rhs.amount),
                self.rhs.currency.code,
            ]
            return sql, params

        # Normal lookup without currency check
        return f"{lhs} {self.operator} {rhs}", lhs_params + rhs_params


class MoneyExactLookup(MoneyCurrencyLookupMixin, Lookup):  # type: ignore[type-arg]
    lookup_name = "exact"
    operator = "="


class MoneyLtLookup(MoneyCurrencyLookupMixin, Lookup):  # type: ignore[type-arg]
    lookup_name = "lt"
    operator = "<"


class MoneyLteLookup(MoneyCurrencyLookupMixin, Lookup):  # type: ignore[type-arg]
    lookup_name = "lte"
    operator = "<="


class MoneyGtLookup(MoneyCurrencyLookupMixin, Lookup):  # type: ignore[type-arg]
    lookup_name = "gt"
    operator = ">"


class MoneyGteLookup(MoneyCurrencyLookupMixin, Lookup):  # type: ignore[type-arg]
    lookup_name = "gte"
    operator = ">="
