class IncorrectMoneyInputError(Exception):
    """Invalid input for the Money object"""


class CurrencyMismatchException(ArithmeticError):
    """Raised when an operation is not allowed between differing currencies"""


class InvalidOperationException(TypeError):
    """Raised when an operation is never allowed"""


class UnsupportedLookupError(Exception):
    """Unsupported lookups using Money object"""
