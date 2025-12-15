from decimal import Decimal
from unittest import TestCase

from money.money import (
    Money,
    CURRENCY,
    Currency,
    CurrencyMismatchException,
    InvalidOperationException,
    IncorrectMoneyInputError,
)


def test_string_parse():
    value = Money.from_string("USD 100.0")
    assert value.amount == Decimal("100.0")
    assert value.currency == "USD"
    assert value.currency == CURRENCY["USD"]


def test_string_parse_default_currency():
    value = Money.from_string("100.0")
    assert value.amount == Decimal("100.0")
    assert value.currency == "XXX"
    assert value.currency == CURRENCY["XXX"]


class MoneyTestCase(TestCase):
    """
    Tests of the Money class
    """

    def test_creation(self):
        """
        We should be able to create a money object with inputs
        similar to a Decimal type
        """
        result = Money(10, "USD")
        self.assertEqual(result.amount, 10)

        result = Money(-10, "USD")
        self.assertEqual(result.amount, Decimal("-10"))

        result = Money(Decimal("10"), "USD")
        self.assertEqual(result.amount, Decimal("10"))

        result = Money(Decimal("-10"), "USD")
        self.assertEqual(result.amount, Decimal("-10"))

        result = Money("10.50", "USD")
        self.assertEqual(result.amount, Decimal("10.50"))

        result = Money("-10.50", "USD")
        self.assertEqual(result.amount, Decimal("-10.50"))

        result = Money("10.50", "USD")
        self.assertEqual(result.amount, Decimal("10.50"))

        result = Money("-10.50", "USD")
        self.assertEqual(result.amount, Decimal("-10.50"))

    def test_creation_unspecified_currency(self):
        """
        Same thing as above but with the unspecified 'xxx' currency
        """

        result = Money(10)
        self.assertEqual(result.amount, 10)

        result = Money(-10)
        self.assertEqual(result.amount, Decimal("-10"))

        result = Money(Decimal("10"))
        self.assertEqual(result.amount, Decimal("10"))

        result = Money(Decimal("-10"))
        self.assertEqual(result.amount, Decimal("-10"))

        result = Money("10.50")
        self.assertEqual(result.amount, Decimal("10.50"))

        result = Money("-10.50")
        self.assertEqual(result.amount, Decimal("-10.50"))

    def test_creation_unspecified_amount(self):
        """
        Same thing as above but with the unspecified 'xxx' currency
        """

        result = Money(currency="USD")
        self.assertEqual(result.amount, 0)
        self.assertEqual(result.currency.code, "USD")

    def test_creation_internal_types(self):
        curr = Currency(code="AAA", name="My Currency")
        result = Money(Decimal("777"), currency=curr)
        self.assertEqual(result.amount, Decimal("777"))
        self.assertEqual(result.currency.code, "AAA")
        self.assertEqual(result.currency.name, "My Currency")

    def test_creation_parsed(self):
        result = Money("XXX -10.50")
        self.assertEqual(result.amount, Decimal("-10.50"))
        self.assertEqual(result.currency.code, "XXX")

        result = Money("USD -11.50")
        self.assertEqual(result.amount, Decimal("-11.50"))
        self.assertEqual(result.currency.code, "USD")

        result = Money("JPY -12.50")
        self.assertEqual(result.amount, Decimal("-12.50"))
        self.assertEqual(result.currency.code, "JPY")

    def test_creation_parsed_conflicting(self):
        # currency declaration two ways
        self.assertRaises(IncorrectMoneyInputError, lambda: Money("USD 123", "JPY"))

    def test_creation_parsed_malformed(self):
        self.assertRaises(IncorrectMoneyInputError, lambda: Money("USD 123 USD"))

    def test_equality(self):
        ten_bucks = Money(10, "USD")
        a_hamilton = Money(10, "USD")

        juu_en = Money(10, "JPY")

        nada = Money(0, "USD")

        # Scalars cannot be compared to Money class
        self.assertFalse(ten_bucks == 10)
        # unless it is 0
        self.assertTrue(nada == 0)

        # Money is equal to money of the same type
        self.assertTrue(ten_bucks == a_hamilton)

        # But not different currencies
        self.assertFalse(ten_bucks == juu_en)

    def test_subtraction(self):
        result = Money(10, "USD") - Money(3, "USD")
        self.assertEqual(result, Money(7, "USD"))
        self.assertEqual(result.amount, Decimal("7"))
        self.assertEqual(result.currency, CURRENCY["USD"])

    def test_negative_subtraction(self):
        result = Money(3, "USD") - Money(10, "USD")
        self.assertEqual(result, Money(-7, "USD"))
        self.assertEqual(result.amount, Decimal("-7"))
        self.assertEqual(result.currency, CURRENCY["USD"])

    def test_amount_attribute(self):
        value = Money(101, "USD")
        self.assertEqual(value.amount, 101)

    def test_currency_attribute(self):
        value = Money(101, "USD")
        self.assertEqual(value.currency, "USD")
        value = Money(101, "JPY")
        self.assertEqual(value.currency, "JPY")


class InvalidMoneyOperationTestCase(TestCase):
    """
    Tests of invalid operations on the Money class. All of these are tests of
    undefined behavior. For the most part we expect an exception to be raised.

    In general, we are taking the stance that Money operations should typically
    be conservative. Please see the README for more information.

    """

    def test_differing_currency_subtraction(self):
        self.assertRaises(
            CurrencyMismatchException, lambda: Money(10, "JPY") - Money(3, "USD")
        )

    def test_differing_currency_addition(self):
        self.assertRaises(
            CurrencyMismatchException, lambda: Money(10, "JPY") + Money(3, "USD")
        )

    def test_division_is_invalid(self):
        # Division of two currencies doesn't really make sense
        self.assertRaises(
            InvalidOperationException, lambda: Money(10, "USD") / Money(3, "USD")
        )

    def test_differing_currency_division(self):
        self.assertRaises(
            InvalidOperationException, lambda: Money(10, "JPY") / Money(3, "USD")
        )

    def test_multiplication_is_invalid(self):
        # Multiplication of two currencies doesn't really make sense
        self.assertRaises(
            InvalidOperationException, lambda: Money(10, "USD") * Money(3, "USD")
        )

    def test_differing_currency_multiplication(self):
        # Differing currencies should not matter
        self.assertRaises(
            InvalidOperationException, lambda: Money(10, "JPY") * Money(3, "USD")
        )

    def test_mutation_of_amount(self):
        with self.assertRaises(AttributeError):
            Money(10, "JPY").amount = 3  # type: ignore[misc]

    def test_mutation_of_currency(self):
        with self.assertRaises(AttributeError):
            Money(10, "JPY").currency = "USD"  # type: ignore[misc]
