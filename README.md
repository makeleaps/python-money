# python-money

Python library for working with money and currencies, with Django integration.

## Features

- **Type-safe money operations** - Prevent errors like adding USD and EUR
- **Immutable currency handling** - Based on ISO-4217 standard
- **Full type annotations** - 100% typed with mypy strict mode
- **Django model field** - Store monetary values with proper currency tracking
- **Conservative math operations** - Explicit currency conversions, no implicit behavior

## Requirements

- **Python:** 3.10 or higher
- **Django:** 4.0.10 or 4.2.7

## Installation
```bash
pip install git+https://github.com/makeleaps/python-money.git@v2.0.0
```

Or add to your `pyproject.toml`:
```toml
dependencies = [
    "python-money@git+https://github.com/makeleaps/python-money.git@v2.0.0"
]
```

## Quick Start
```python
from money import Money, CURRENCY

# Create money values
usd_price = Money('19.99', CURRENCY['USD'])
usd_tax = Money('2.00', CURRENCY['USD'])

# Safe arithmetic
usd_total = usd_price + usd_tax  # USD 21.99

# Prevents currency mistakes
eur = Money('10.00', CURRENCY['EUR'])
usd_price + eur  # Raises CurrencyMismatchException
```

## About This Fork

This fork (rooted at poswald/python-money) takes a **conservative approach** to money operations:

- ✅ Explicit currency conversions only (no implicit conversion)
- ✅ No global state or default currencies
- ✅ Type-safe operations with full mypy coverage
- ✅ Modern tooling (uv, ruff, pytest, nox)

**Not a drop-in replacement** - If you're migrating from another fork, review the [CHANGELOG.md](CHANGELOG.md) for breaking changes, especially around imports and removed implicit conversion features.

## Usage

This application contains several classes and functions that make dealing with money easier and less error-prone.

### Currency

The `Currency` dataclass represents a type of currency with its code, ISO number, name, and countries:
```python
Currency(code='BZD', numeric='084', name='Belize Dollar', countries=['BELIZE'])
```

Use the `CURRENCY` constant to access all ISO-4217 currencies:
```python
from money import CURRENCY

print(CURRENCY['GBP'].name)  # 'Pound Sterling'
print(CURRENCY['USD'].code)  # 'USD'
```

### Money

The `Money` dataclass handles arithmetic with currency values safely. It wraps Python's `Decimal` type and prevents common mistakes like adding different currencies or multiplying two money values:
```python
from money import Money, CURRENCY

# Create money values
usd = Money(amount=10.00, currency=CURRENCY['USD'])
print(usd)  # USD 10.00

jpy = Money(amount=2000, currency=CURRENCY['JPY'])
print(jpy)  # JPY 2000.00

# Safe operations
print(usd * 5)      # USD 50.00
print(usd + usd)    # USD 20.00

# Prevented operations
print(jpy * usd)    # TypeError: can not multiply monetary quantities
print(jpy > usd)    # TypeError: can not compare different currencies
```

## Math Operations and Equality

### Currency Comparison
- `USD 0 == EUR 0` → **False** (different currencies)
- `USD 0 == 0` → **True** (can compare to zero)
- `USD 10 == EUR 10` → **Raises `CurrencyMismatchException`**

You can only compare money with the same currency or with `0`.

### Supported Operations

**Allowed:**
```python
Money(10, 'USD') + Money(5, 'USD')   # Money(15, 'USD')
Money(10, 'USD') - Money(5, 'USD')   # Money(5, 'USD')
Money(10, 'USD') * 3                 # Money(30, 'USD')
Money(10, 'USD') / 2                 # Money(5, 'USD')
```

**Not allowed:**
```python
Money(10, 'USD') + Money(5, 'EUR')   # CurrencyMismatchException
Money(10, 'USD') * Money(3, 'USD')   # InvalidOperationException
Money(10, 'USD') / Money(2, 'USD')   # InvalidOperationException
```

### Why Not Money / Money?

Dividing two `Money` objects is ambiguous:
- Should `Money(9, 'USD') / Money(3, 'USD')` return `Money(3, 'USD')`?
- Or `Decimal('3')`?
- Or `Money(3, 'XXX')` with undefined currency?

To keep operations explicit, this raises `InvalidOperationException`. If you need to divide amounts, use:
```python
# Get a decimal ratio
Money(9, 'USD').amount / Money(3, 'USD').amount  # Decimal('3')
```

This makes your intent clear and prevents accidental currency errors.

## Boolean Evaluation

`Money` behaves like Python's `Decimal` in boolean contexts:
```python
bool(Money('0', 'USD'))     # False
bool(Money('0.01', 'USD'))  # True
bool(Money('1', 'USD'))     # True
```

To check if a `Money` object exists, compare to `None`:
```python
if amount is None:
    amount = Money(0, 'USD')
```

## Django Integration

Optional Django support is included for convenience.

### MoneyField

Add a currency field to your models:
```python
from money.contrib.django.models.fields import MoneyField

class Product(models.Model):
    price = MoneyField(default=0, max_digits=12, decimal_places=2)
```

This creates two database columns:
- `price` - stores the amount (e.g., `numeric(12,2)`)
- `price_currency` - stores the currency code (e.g., `varchar(3)`)

Usage:
```python
product = Product.objects.get(id=123)
print(product.price)  # USD 199.99
```

### Fixtures

When using fixtures, specify amount and currency separately:
```json
{
    "pk": 1,
    "model": "myapp.product",
    "fields": {
        "price": "123.45",
        "price_currency": "USD"
    }
}
```

### PostgreSQL Precision

The `MoneyField` uses PostgreSQL's `numeric` type to preserve user-entered precision. Values like `3`, `3.0`, and `3.000` are stored exactly as entered.

### SQLite Limitation

SQLite coerces `NUMERIC` values like `100.00` into integers, losing decimal precision. If you need to preserve user-entered precision, PostgreSQL is recommended over SQLite.

[sqlite_datatypes]: http://www.sqlite.org/datatype3.html

## Local Development

### Setup

1. **Clone the repository:**
```bash
   git clone https://github.com/makeleaps/python-money.git
   cd python-money
```

2. **Install `uv` and dependencies:**
```bash
   # Install uv (if not already installed)
   
   # Install all dependencies including dev dependencies
   uv sync --dev
```

3. **Activate the environment:**
```bash
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate     # On Windows
```

### Running Tools

**Linting:**
```bash
uv run ruff check .
uv run ruff format .
```

**Type checking:**
```bash
uv run mypy .
```

**Tests:**
```bash
uv run pytest
```

**Install pre-commit hooks:**
```bash
uv run pre-commit install
```

Once installed, pre-commit will automatically run `ruff`, `mypy`, and `pytest` before each commit.

## ChangeLogs

See [CHANGELOG.md](CHANGELOG.md) for release history.
