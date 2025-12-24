# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0]

**Note:**
This release modernizes the repository with current Python and Django best practices.
It includes breaking changes to imports and drops support for Python 2 and Python 3.9 and lower.

### Added
- `uv` as the package manager with `pyproject.toml` for dependency management
  - **Dependency (required):**
    - django==4.0.10
  - **Dev Dependencies:**
      - `ruff` as the primary linter
      - `mypy` as the primary type checker with strict mode enabled
      - `django-stubs` for Django type stubs
      - `pytest` as the primary test framework
      - `nox` for testing across multiple Python and Django versions
      - `pre-commit` hooks for `ruff`, `mypy`, and `nox`
- GitHub Actions workflow running `ruff`, `mypy`, and `nox`
- `py.typed` marker for proper type inference in dependent projects
- Custom Django Lookups: `MoneyExactLookup`, `MoneyGteLookup`, `MoneyGtLookup`, `MoneyLteLookup`, `MoneyLtLookup` (ref: [Django custom lookups](https://docs.djangoproject.com/en/4.0/howto/custom-lookups/))
- Pull request template
- Test coverage for Django lookups in `money/tests/test_django_lookups.py`
- Test coverage for nullability in `money/tests/test_money_nullability.py`

### Changed
- Updated to Python 3.10 (tracked in `.python-version`)
- Dependency updated to Django `4.0.10`
- Updated entire codebase to be 100% typed, passing `mypy` in strict mode
- `Currency` is now a frozen Python dataclass for enforced immutability
- `Money` is now a Python dataclass
- Refactored some tests from `TestCase` to function-based tests
- **Reorganized project structure:**
  - Moved `Currency` to `money/dataclasses/currency.py`
  - Moved `Money` to `money/dataclasses/money.py`
  - Moved `CURRENCY` to `money/constants.py`
  - Moved all custom exceptions to `money/exceptions.py`
  - Moved `MoneyFieldProxy` to `money/contrib/django/models/proxy.py`

### Removed
- Support for Python 2
- Support for Python 3.9 and lower
- `MoneyManager` class (replaced with custom Django Lookups)
- `QuerysetWithMoney` class (replaced with custom Django Lookups)

### Fixed
- Bug in lookup operations using `Money` objects directly, where amount was compared without checking currency ([PR #13](https://github.com/makeleaps/python-money/pull/13))
- Bug where using a custom Manager in a Django Model would override `MoneyManager`, causing lookup operations to compare amounts without checking currency ([PR #13](https://github.com/makeleaps/python-money/pull/13))

### Testing
Tested and verified compatibility with:
- Python 3.10 + Django 4.0.10
- Python 3.11 + Django 4.0.10
- Python 3.10 + Django 4.2.27
- Python 3.11 + Django 4.2.27

**Breaking Changes:**

1. **Import paths changed** - Import directly from `money` instead of `money.money`:
   ```python
   # Old (no longer works)
   from money.money import Money, Currency, CURRENCY, IncorrectMoneyInputError
   
   # New (required)
   from money import Money, Currency, CURRENCY, IncorrectMoneyInputError
   ```
   
   For `NotSupportedLookup`:
   ```python
   from money import NotSupportedLookup
   ```

2. **Type checking** - Added `py.typed` marker enables `mypy` type inference in dependent projects. You may need to update type annotations in your codebase to work with the new complete type information.

3. **Django ORM** - Removed `MoneyManager` and `QuerysetWithMoney`. The package now uses Django's custom Lookup API. Existing queries should work without changes, but custom manager extensions may need updates.

## [1.1]

### Added
- Python 3 compatibility

### Fixed
- Queryset returning the wrong value when running in Django 1.8


## [1.0.1] - (tagged 0.3.3)

### Added
- Support for the `db_column` parameter

## [1.0.0] (tagged 0.3.2)

**Note:** 
This fork of the project is now going to be version-managed separate from other forks.
This is the first release that we consider to be fully 'production ready' for our purposes.
Future changes will follow semantic versioning.

Most of these are breaking changes, so please check accordingly.

### Added
- Added a full test suite
- Added coverage report generation
- Added support for division operations (Python 2 and 3)
- Added support for boolean operations (Python 2 and 3). 

### Changed
- Division now returns Money object
- Fixed several bugs in mathematical operations
- Better use of standard python packaging
- Work toward making the `Money` immutable so it can safely be used as a
  field default
- Unsupported django ORM lookups now raise an exception that is a subclass
  of `TypeError` as recommended by the django docs
- The `InvalidOperationException` now extends `TypeError` instead of the
  `ArithmeticError` exception
- The `Money.from_string` method is now a classmethod

## Removed
- Removed support for floor division
- Removed `set_default_currency` global function
- Removed implicit currency conversion methods: `convert_to_default`,
  `convert_to`, and `allocate`
- Removed custom override of the `%` operator
- Removed currency exchange rate form the `Currency` object and the related `set_exchange_rate()` method.

## [0.2.0]

### Fixed
- Issue with South introspection rule for MoneyField (similar to South #327)
- **Note:** You may need to generate a new schema migration if upgrading

## [0.1.0]

### Added
- Initial release

