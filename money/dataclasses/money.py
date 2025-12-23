import dataclasses
from decimal import Decimal
from typing import Union

from money.constants import CURRENCY, DEFAULT_CURRENCY
from money.dataclasses.currency import Currency
from money.exceptions import (
    CurrencyMismatchException,
    IncorrectMoneyInputError,
    InvalidOperationException,
)

CompareWithMoney = Union["Money", Decimal | int | float | str]


@dataclasses.dataclass
class Money:
    """
    An amount of money with an optional currency

    Pass in the amount and currency during initialization. Amounts will be
    represented as Decimals internally.

    The following are supported:

        Money()                 # XXX 0
        Money(123)              # XXX 123
        Money('123.00')         # XXX 123.00
        Money('123.00', 'USD')  # XXX 123.00
        Money('123.00', 'USD')  # USD 123.00
        Money('123', 'JPY')     # JPY 123
        Money('123.0', 'JPY')   # JPY 123.0

        # Parsed string
        Money('USD 123.00')     # USD 123.00

        # Decimal
        Money(Decimal('123.0'), 'JPY')   # JPY 123.0

        # kwargs
        Money(amount='123.0', currency='JPY')   # JPY 123.0

        # native types
        Money(Decimal('123.0'), Currency(code='AAA', name=u'My Currency')  # AAA 123.0

    """

    _amount: Decimal
    _currency: Currency

    @classmethod
    def _from_string(cls, value: str | int | float) -> tuple[Decimal, Currency]:
        s = str(value).strip()
        try:
            amount = Decimal(s)
            currency = DEFAULT_CURRENCY
        except:  # noqa: E722
            try:
                currency = CURRENCY[s[:3].upper()]
                amount = Decimal(s[3:].strip())
            except:  # noqa: E722
                raise IncorrectMoneyInputError(
                    "The value '%s' is not properly formatted as 'XXX 123.45' " % s
                )
        return amount, currency

    @classmethod
    def from_string(cls, value: str) -> "Money":
        """
        Parses a properly formatted string. The string should be formatted as
        given by the repr function: 'USD 123.45'
        """
        return Money(*cls._from_string(value))

    def _currency_check(self, other: "Money") -> None:
        """Compare the currencies matches and raise if not"""
        if self._currency != other.currency:
            raise CurrencyMismatchException(
                "Currency mismatch: %s != %s" % (self._currency, other.currency)
            )

    def __init__(
        self,
        amount: str | Decimal | int | float | None = None,
        currency: str | Currency | None = None,
    ):
        if isinstance(amount, Decimal):
            self._amount = amount
        else:
            try:
                self._amount = Decimal(amount or 0)
            except:  # noqa: E722
                # Decimal couldn't initialize it
                try:
                    # check for the odd case of Money("USD 123.00", "JPY")
                    if currency:
                        raise IncorrectMoneyInputError(
                            "Initialized with conflicting currencies %s %s"
                            % (
                                currency.code
                                if isinstance(currency, Currency)
                                else currency,
                                self._amount,
                            )
                        )

                    self._amount, currency = self._from_string(amount or 0)
                except:  # noqa: E722
                    raise IncorrectMoneyInputError(
                        "Cannot initialize with amount %s" % amount
                    )

        # at this point we have amount and possibly a currency
        if not currency:
            currency = DEFAULT_CURRENCY

        if not isinstance(currency, Currency):
            currency = CURRENCY[str(currency).upper()]

        self._currency = currency
        assert isinstance(self._amount, Decimal)
        assert isinstance(self._currency, Currency)

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def currency(self) -> Currency:
        return self._currency

    def __str__(self) -> str:
        return "{} {}".format(self._currency, self._amount)

    def __repr__(self) -> str:
        return str(self)

    def __float__(self) -> float:
        return float(self._amount)

    def __int__(self) -> int:
        return int(self._amount)

    def __pos__(self) -> "Money":
        return Money(amount=self._amount, currency=self._currency)

    def __neg__(self) -> "Money":
        return Money(amount=-self._amount, currency=self._currency)

    def __add__(self, other: CompareWithMoney) -> "Money":
        if isinstance(other, Money):
            self._currency_check(other)
            return Money(amount=self._amount + other.amount, currency=self._currency)
        else:
            return Money(
                amount=self._amount + Decimal(str(other)), currency=self._currency
            )

    def __sub__(self, other: CompareWithMoney) -> "Money":
        if isinstance(other, Money):
            self._currency_check(other)
            return Money(amount=self._amount - other.amount, currency=self._currency)
        else:
            return Money(
                amount=self._amount - Decimal(str(other)), currency=self._currency
            )

    def __rsub__(self, other: CompareWithMoney) -> None:
        # In the case where both values are Money, the left hand one will be
        # called. In the case where we are subtracting Money from another
        # value, we want to disallow it
        raise TypeError("Cannot subtract Money from %r" % other)

    def __mul__(self, other: CompareWithMoney) -> "Money":
        if isinstance(other, Money):
            raise InvalidOperationException("Cannot multiply monetary quantities")
        return Money(amount=self._amount * Decimal(str(other)), currency=self._currency)

    def __truediv__(self, other: int | Decimal) -> "Money":
        """
        We allow division by non-money numeric values but dividing by
        another Money value is undefined
        """
        if isinstance(other, Money):
            raise InvalidOperationException("Cannot divide two monetary quantities")
        return Money(amount=self._amount / other, currency=self._currency)

    __div__ = __truediv__

    def __floordiv__(self, other: CompareWithMoney) -> None:
        raise InvalidOperationException(
            "Floor division not supported for monetary quantities"
        )

    def __rtruediv__(self, other: CompareWithMoney) -> None:
        raise InvalidOperationException("Cannot divide by monetary quantities")

    __rdiv__ = __rtruediv__

    # Commutative operations
    __radd__ = __add__
    __rmul__ = __mul__

    # Boolean
    def __bool__(self) -> bool:
        return self._amount != 0

    __nonzero__ = __bool__

    # Comparison operators
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Money):
            return bool(
                (self._amount == other.amount) and (self._currency == other.currency)
            )

        if isinstance(other, (Decimal, int, float, str)):
            # Allow comparison to 0
            if (other == 0) and (self._amount == 0):
                return True
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self, other: CompareWithMoney) -> bool:
        if isinstance(other, Money):
            self._currency_check(other)
            return self._amount < other.amount
        else:
            return self._amount < Decimal(str(other))

    def __gt__(self, other: CompareWithMoney) -> bool:
        if isinstance(other, Money):
            self._currency_check(other)
            return self._amount > other.amount
        else:
            return self._amount > Decimal(str(other))

    def __le__(self, other: CompareWithMoney) -> bool:
        return self < other or self == other

    def __ge__(self, other: CompareWithMoney) -> bool:
        return self > other or self == other
