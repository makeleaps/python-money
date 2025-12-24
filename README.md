python-money
============

Primitives for working with money and currencies in Python

Compatibility
=============

This fork of python-money (rooted at poswald/python-money) is significantly different from other versions in the family tree.
If you plan on using it, please be aware that it most likely won't be a drop-in replacement.

We have made several changes to be more conservative about operations, remove implicit conversion of currency, remove global state, added a postgres specific field, and a `py.test` based test suite among other changes.

You are free to use this version but please look at other forks as well as they may better suit your use case.

Requirements
============

We currently support Django version `4.0.10` or `4.2.27`, with minimum Python version `3.10`.

Installation
============

Install this project directly from the git repository using pip:

    $ pip install -e git+http://github.com/makeleaps/python-money.git@2.0.0#egg=python-money

Usage
=====

This application contains several classes and functions that make dealing with money easier and less error-prone.

### Currency dataclass

The Currency dataclass is used to represent a type of Currency. 
It contains values for the currency's code, ISO number, name and the country it's used in.

    Currency(code='BZD', numeric='084', name='Belize Dollar', countries=['BELIZE'])

Use `CURRENCY` for all ISO-4217 currencies:

    >>> from money import CURRENCY
    >>> print(CURRENCY['GBP'].name)
    Pound Sterling

### Money dataclass

The Money dataclass is available for doing arithmetic on values in defined currencies.
It wraps the python Decimal type and gives you several convenience methods.
Using this prevents you from making mistakes like adding Pounds and Dollars together, multiplying two money values or comparing different currencies.


    >>> usd = Money(amount=10.00, currency=CURRENCY['USD'])
    >>> print usd
    USD 10.00

    >>> jpy = Money(amount=2000, currency=CURRENCY['JPY'])
    >>> print jpy
    JPY 2000.00

    >>> print jpy * usd
    Traceback (most recent call last):
      File "<console>", line 1, in <module>
      File "/python-money/money/Money.py", line 79, in __mul__
        raise TypeError, 'can not multiply monetary quantities'
    TypeError: can not multiply monetary quantities

    >>> print jpy > usd
    Traceback (most recent call last):
      File "<console>", line 1, in <module>
      File "/Users/poswald/Projects/python-money/money/Money.py", line 137, in __gt__
        raise TypeError, 'can not compare different currencies'
    TypeError: can not compare different currencies

    >>> print 1 % usd
    USD  0.10

    >>> print usd * 5
    USD 50.00

    >>> print (usd * 5).allocate((50,50))
    [USD 25.00, USD 25.00]
    >>> print (jpy * 5).allocate((50,50))
    [JPY 5000.00, JPY 5000.00]

### Default Currency

This package assumes that you have a preferred default currency. Somewhere in
your software's initialization you should set that currency:

    >>> from money.money import set_default_currency
    >>> set_default_currency(code='USD')
    >>> print Money(amount=23.45)
    USD 23.45

If you don't you will get a non-specified 'XXX' currency:

    >>> print Money(amount=23.45)
    XXX 23.45

A Note About Equality and Math Operations
-----------------------------------------

The way equality is currently implemented, `USD 0` is not equal to `EUR 0` however,
`USD 0` is considered equal to `0`. This means you can only compare similar
currencies to each other, but it is safe to compare a currency to the value `0`.

Comparing two differing currencies is undefined and will raise
a `money.CurrencyMismatchException`. Prior versions of this project would do an
implicit conversion to a 'base' currency using a defined conversion rate and
perform the operation. We believe this is unexpected behavior, and it is better
to let the user do that conversion themselves for the cases where they know they
are comparing differing currencies.

Similarly, we take a conservative approach to certain math operations. For
example, `Money(10, 'USD') - Money(3, 'JPY')` is not allowed due to differing
currencies.

Both `Money(3, 'USD') * Money(3, 'USD')` and `Money(9, 'USD') / Money(3, 'USD')`
are undefined. There are 3 conceivable ways to handle division:

    Money(9, 'USD') / Money(3, 'USD') # Money(3, 'XXX') # where 'XXX' denotes undefined currency
    Money(9, 'USD') / Money(3, 'USD') # Decimal('3')
    Money(9, 'USD') / Money(3, 'USD') # raise money.InvalidOperationException

We have chosen the last option as it is the most conservative option. You can
always emulate the first two by using the underlying amounts:

    Money(9, 'USD').amount / Money(3, 'USD').amount # Decimal('3')
    Money(Money(9, 'USD').amount / Money(3, 'USD').amount) # Money('3', 'XXX')

This makes the intention of the code more clear.

As an exception to that, we allow diving a Money object by a number:

    Money(9, 'USD') / 3 # Money(3, 'USD')


Boolean Evaluation
------------------

When evaluated in a boolean context, the `Money` type behaves similar to the
python `Decimal` class:

    bool(Decimal('0'))    # False
    bool(Decimal('0.1'))  # True

    bool(Money('0', 'USD'))    # False
    bool(Money('0.01', 'USD')) # True
    bool(Money('1'))           # True

To test for the existence of the objects, compare the value to `None`:

    if amount is None:
        amount = Money(0)

Django
======

This package includes some classes as a convenience to Django users. These are
entirely optional.

### Model Field

Add a currency field to your models. This field takes similar parameters as
the Django DecimalField:

    from money.contrib.django.models.fields import MoneyField

    class Thing(models.Model):
        ...
        price = MoneyField(default=0, max_digits=12, decimal_places=2)
        ...

Now run `./manage.py dbsync` or South migrate. Your database table will contain a field for holding the value and a second field for the currency type.
In PostgreSQL, it might look like this:

    price          | numeric(12,2)          | not null default NULL::numeric
    price_currency | character varying(3)   | not null

The value you get from your model will be a `Money` class:

    thing = Thing.objects.get(id=123)
    print repr(thing.price)
    USD  199.99


### User Defined Precision of Decimals in Postgres

It can be difficult to represent decimals exactly as the user entered them with
Django. If you use postgres, you can preserve the user's entered precision by
using the PostgreSQL `numeric` type. Simply use the `InfiniteDecimalField`
class and the value will be stored as entered by the user without having to
define the precision in the model class.

    InfiniteDecimalField

This allows you to store and later retrieve a values like `3`, `3.0`, and
`3.000` without losing the precision. The `MoneyField` class already extends this
by default.


### Fixtures

When loading from or serializing to fixtures, the field class expects the
values to be specified separately:

    ...
    {
        "pk": 1,
        "model": "myapp.mymodel",
        "fields": {
            "price": "123.45",
            "price_currency": "USD",
        }
    },
    ...

You may wish to examine the tests for an example


### Form Field

The form field used by the `models.MoneyField` is also called `MoneyField`


### Running Tests

The test suite requires `py.test`, `django` and several other libraries to be
installed. They will be downloaded and installed automatically when run.

Tests can be run via the `setup.py` script:

    $ python setup.py test

If you wish to contribute code, please run these tests to ensure nothing breaks.


SQLite
------

Due to [the way SQLite handles][sqlite_datatypes] `NUMERIC` values, a value
like `100.00` will be coerced into an integer. This means the user entered
precision is lost when saving to the database. The alternative would be to
store the value as a `TEXT` affinity but then ORM comparison operations will
break.

If your application always specified the precision, this isn't a problem. If
you need to maintain the user's precision, then SQLite is not recommended.

[sqlite_datatypes]: http://www.sqlite.org/datatype3.html


TODO
====

* Add more currency symbols to Currency class
* Add number of decimal places to all Currencies. Who wants to help? :-)

CHANGELOG
===

See [CHANGELOG.md](CHANGELOG.md) for release history.
