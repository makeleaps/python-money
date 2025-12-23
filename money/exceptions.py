class IncorrectMoneyInputError(Exception):
    """Invalid input for the Money object"""


class CurrencyMismatchException(ArithmeticError):
    """Raised when an operation is not allowed between differing currencies"""


class InvalidOperationException(TypeError):
    """Raised when an operation is never allowed"""


class NotSupportedLookup(TypeError):
    def __init__(self, lookup_name: str):
        super().__init__()
        self.lookup_name = lookup_name

    def __str__(self) -> str:
        return "Lookup '%s' is not supported for MoneyField" % self.lookup_name
