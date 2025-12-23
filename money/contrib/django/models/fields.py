from decimal import Decimal
from typing import TYPE_CHECKING, Any

from django.db import models
from django.db.models import Lookup
from django.utils.translation import gettext_lazy

from money.contrib.django import forms
from money.money import Currency, Money

if TYPE_CHECKING:
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.models.expressions import Col
    from django.db.models.sql.compiler import SQLCompiler


__all__ = ("MoneyField", "currency_field_name", "NotSupportedLookup")


def currency_field_name(name: str) -> str:
    return "%s_currency" % name


def currency_field_db_column(db_column):
    return None if db_column is None else "%s_currency" % db_column


SUPPORTED_LOOKUPS = ("exact", "lt", "gt", "lte", "gte", "isnull")


class NotSupportedLookup(TypeError):
    def __init__(self, lookup):
        super().__init__()
        self.lookup = lookup

    def __str__(self):
        return "Lookup '%s' is not supported for MoneyField" % self.lookup


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
            self, compiler: "SQLCompiler", connection: "BaseDatabaseWrapper"
        ) -> tuple[str, list[Any]]: ...

        def process_rhs(
            self, compiler: "SQLCompiler", connection: "BaseDatabaseWrapper"
        ) -> tuple[str, list[Any]]: ...

    def as_sql(
        self, compiler: "SQLCompiler", connection: "BaseDatabaseWrapper"
    ) -> tuple[str, list[Any]]:
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)

        # Check if the original rhs value (before processing) is a Money object
        if isinstance(self.rhs, Money):
            # Get the currency field column name
            currency_field = currency_field_name(self.lhs.field.name)
            currency_column = self.lhs.field.model._meta.get_field(
                currency_field
            ).column

            # Build SQL that checks both amount and currency
            # Get the table alias from lhs
            table_name = self.lhs.alias
            currency_lhs_sql = f"{compiler.quote_name_unless_alias(table_name)}.{compiler.quote_name_unless_alias(currency_column)}"

            # Construct the full condition
            amount_condition = f"{lhs} {self.operator} {rhs}"
            currency_condition = f"{currency_lhs_sql} = %s"

            sql = f"({amount_condition} AND {currency_condition})"
            params = lhs_params + [self.rhs.amount, self.rhs.currency.code]

            return sql, params
        else:
            # Normal lookup without currency check
            return f"{lhs} {self.operator} {rhs}", lhs_params + rhs_params


class MoneyExactLookup(MoneyCurrencyLookupMixin, Lookup):
    lookup_name = "exact"
    operator = "="


class MoneyLtLookup(MoneyCurrencyLookupMixin, Lookup):
    lookup_name = "lt"
    operator = "<"


class MoneyLteLookup(MoneyCurrencyLookupMixin, Lookup):
    lookup_name = "lte"
    operator = "<="


class MoneyGtLookup(MoneyCurrencyLookupMixin, Lookup):
    lookup_name = "gt"
    operator = ">"


class MoneyGteLookup(MoneyCurrencyLookupMixin, Lookup):
    lookup_name = "gte"
    operator = ">="


class MoneyFieldProxy(object):
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
        self.field: "MoneyField" = field
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

    def __get__(self, obj: models.Model, *args):
        if obj is None:
            return self
        amount, currency = self._get_values(obj)
        if amount is None:
            return None
        return Money(amount, currency)

    def __set__(self, obj: models.Model, value):
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


class InfiniteDecimalField(models.DecimalField):
    def db_type(self, connection):
        engine = connection.settings_dict["ENGINE"]

        if "postgresql" in engine:
            return "numeric"

        return super().db_type(connection=connection)

    def get_db_prep_save(self, value, *args, **kwargs):
        """
        Called when the Field value must be saved to the database. As the
        default implementation just calls get_db_prep_value(), you shouldn't
        need to implement this method unless your custom field needs a special
        conversion when being saved that is not the same as the conversion used
        for normal query parameters
        """

        # The superclass DecimalField get_db_prep_save will add decimals up to
        # the precision in the field definition. The point of this class is to
        # use the user-specified precision up to that limit instead. For that
        # reason we will call get_db_prep_value instead
        return self.get_db_prep_value(value, *args, **kwargs)


class CurrencyField(models.CharField):
    """
    This field will be added to the model behind the scenes to hold the
    currency. It is used to enable outputting of currency data as a separate
    value when serializing to JSON.
    """

    def value_to_string(self, obj):
        """
        When serializing, we want to output as two values. This will be just
        the currency part as stored directly in the database.
        """
        value = self.value_from_object(obj)
        return value


class MoneyField(InfiniteDecimalField):
    description = gettext_lazy("An amount and type of currency")
    currency_field_name: str

    # Don't extend SubfieldBase since we need to have access to both fields when
    # to_python is called. We need our code there instead of subfieldBase
    # __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        # We add the currency field except when using frozen south orm. See introspection rules below.
        default_currency = kwargs.pop("default_currency", "")
        default = kwargs.get("default", None)
        self.add_currency_field = not kwargs.pop("no_currency_field", False)

        self.blankable = kwargs.get("blank", False)

        if isinstance(default, Money):
            self.default_currency = default.currency  # use the default's currency
            kwargs["default"] = default.amount
        else:
            self.default_currency = default_currency or ""  # use the kwarg passed in

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["no_currency_field"] = True
        return name, path, args, kwargs

    # Implementing to_python should not be needed because we are directly
    # assigning the attributes to the model with the proxy class. Some parts
    # of the model forms code still tries to call to_python on the field
    # directly which will coerce the Money value into a string
    # representation. To handle this, we're checking for string and seeing if
    # we can split it into two pieces. Otherwise, we assume we're dealing with
    # a string value
    def to_python(self, value):
        if isinstance(value, str):
            try:
                (currency, value) = value.split()
                if currency and value:
                    return Money(value, currency)
            except ValueError:
                pass
        return value

    def contribute_to_class(self, cls, name):
        self.name = name
        self.amount_field_name = name
        self.currency_field_name = currency_field_name(name)

        if self.add_currency_field and not cls._meta.abstract:
            c_field = CurrencyField(
                max_length=3,
                default=self.default_currency,
                editable=False,
                null=False,  # empty char fields should be ''
                blank=self.blankable,
                db_column=currency_field_db_column(self.db_column),
            )
            # Use this field's creation counter for the currency field. This
            # field will get a +1 when we call super
            c_field.creation_counter = self.creation_counter
            cls.add_to_class(self.currency_field_name, c_field)

        # Set ourselves up normally
        super().contribute_to_class(cls, name)

        # As we are not using SubfieldBase, we need to set our proxy class here
        setattr(cls, self.name, MoneyFieldProxy(self))

    def get_db_prep_save(self, value, *args, **kwargs):
        """
        Called when the Field value must be saved to the database. As the
        default implementation just calls get_db_prep_value(), you shouldn't
        need to implement this method unless your custom field needs a special
        conversion when being saved that is not the same as the conversion used
        for normal query parameters
        """
        if isinstance(value, Money):
            value = value.amount

        return super().get_db_prep_save(value, *args, **kwargs)

    def get_db_prep_value(self, value, connection, prepared=False):
        """
        Prepares the value for the database, extracting amount from Money objects.
        """
        if isinstance(value, Money):
            value = value.amount
        return super().get_db_prep_value(value, connection, prepared)

    def get_lookup(self, lookup_name):
        """
        Validates that only supported lookups are used.
        """
        if lookup_name not in SUPPORTED_LOOKUPS:
            raise NotSupportedLookup(lookup_name)
        return super().get_lookup(lookup_name)

    def get_default(self):
        if isinstance(self.default, Money):
            return self.default
        else:
            return super().get_default()

    def value_to_string(self, obj):
        """
        When serializing this field, we will output both value and currency.
        Here we only need to output the value. The contributed currency field
        will get called to output itself
        """
        value = self.value_from_object(obj)
        return value.amount

    def formfield(self, **kwargs):
        defaults = {"form_class": forms.MoneyField}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    @property
    def validators(self):
        # Hack around the fact that we inherit from DecimalField but don't hold
        # Decimals. The real fix is to stop inheriting from DecimalField.
        return []


# Register custom lookups that handle Money objects with currency checking
MoneyField.register_lookup(MoneyExactLookup)
MoneyField.register_lookup(MoneyLtLookup)
MoneyField.register_lookup(MoneyLteLookup)
MoneyField.register_lookup(MoneyGtLookup)
MoneyField.register_lookup(MoneyGteLookup)
