# -*- coding: utf-8 -*-
from decimal import Decimal
from typing import Union

from typing_extensions import Self

from money.exceptions import (
    CurrencyMismatchException,
    IncorrectMoneyInputError,
    InvalidOperationException,
)


class Currency(object):
    code: str = "XXX"
    country: str = ""
    countries: list[str] = []
    name: str = ""
    numeric: str = "999"

    def __init__(
        self,
        code: str = "",
        numeric: str = "999",
        name: str = "",
        symbol: str = "",
        decimals: int = 2,
        countries: list[str] | None = None,
    ):
        if not countries:
            countries = []
        self.code = code
        self.numeric = numeric
        self.name = name
        self.symbol = symbol
        self.decimals = decimals
        self.countries = countries

    def __repr__(self) -> str:
        return self.code

    def __eq__(self, other: Self | str) -> bool:  # type: ignore[override]
        if isinstance(other, Currency):
            return bool(self.code and other.code and (self.code == other.code))
        if isinstance(other, str):
            return self.code == other
        return False

    def __ne__(self, other: Self | str) -> bool:  # type: ignore[override]
        return not self.__eq__(other)


CURRENCY: dict[str, Currency] = {}
CURRENCY["XXX"] = Currency(code="XXX", numeric="999")
DEFAULT_CURRENCY: Currency = CURRENCY["XXX"]

CompareWithMoney = Union["Money", Decimal | int | float | str]


class Money(object):
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
    def __eq__(self, other: CompareWithMoney | None) -> bool:  # type: ignore[override]
        if isinstance(other, Money):
            return bool(
                (self._amount == other.amount) and (self._currency == other.currency)
            )
        # Allow comparison to 0
        if (other == 0) and (self._amount == 0):
            return True
        return False

    def __ne__(self, other: CompareWithMoney | None) -> bool:  # type: ignore[override]
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


#
# Definitions of ISO 4217 Currencies
# Source: http://www.currency-iso.org/
# Symbols: http://www.xe.com/symbols.php
#
# Note that the decimal code of N/A has been mapped to None
CURRENCY["AED"] = Currency(
    code="AED",
    numeric="784",
    decimals=2,
    symbol="",
    name="UAE Dirham",
    countries=["UNITED ARAB EMIRATES"],
)
CURRENCY["AFN"] = Currency(
    code="AFN",
    numeric="971",
    decimals=2,
    symbol="؋",
    name="Afghani",
    countries=["AFGHANISTAN"],
)
CURRENCY["ALL"] = Currency(
    code="ALL",
    numeric="008",
    decimals=2,
    symbol="Lek",
    name="Lek",
    countries=["ALBANIA"],
)
CURRENCY["AMD"] = Currency(
    code="AMD",
    numeric="051",
    decimals=2,
    symbol="",
    name="Armenian Dram",
    countries=["ARMENIA"],
)
CURRENCY["ANG"] = Currency(
    code="ANG",
    numeric="532",
    decimals=2,
    symbol="ƒ",
    name="Netherlands Antillean Guilder",
    countries=["CURA\xc7AO", "SINT MAARTEN (DUTCH PART)"],
)
CURRENCY["AOA"] = Currency(
    code="AOA",
    numeric="973",
    decimals=2,
    symbol="",
    name="Kwanza",
    countries=["ANGOLA"],
)
CURRENCY["ARS"] = Currency(
    code="ARS",
    numeric="032",
    decimals=2,
    symbol="$",
    name="Argentine Peso",
    countries=["ARGENTINA"],
)
CURRENCY["AUD"] = Currency(
    code="AUD",
    numeric="036",
    decimals=2,
    symbol="$",
    name="Australian Dollar",
    countries=[
        "AUSTRALIA",
        "CHRISTMAS ISLAND",
        "COCOS (KEELING) ISLANDS",
        "HEARD ISLAND AND McDONALD ISLANDS",
        "KIRIBATI",
        "NAURU",
        "NORFOLK ISLAND",
        "TUVALU",
    ],
)
CURRENCY["AWG"] = Currency(
    code="AWG",
    numeric="533",
    decimals=2,
    symbol="ƒ",
    name="Aruban Florin",
    countries=["ARUBA"],
)
CURRENCY["AZN"] = Currency(
    code="AZN",
    numeric="944",
    decimals=2,
    symbol="ман",
    name="Azerbaijanian Manat",
    countries=["AZERBAIJAN"],
)
CURRENCY["BAM"] = Currency(
    code="BAM",
    numeric="977",
    decimals=2,
    symbol="KM",
    name="Convertible Mark",
    countries=["BOSNIA AND HERZEGOVINA"],
)
CURRENCY["BBD"] = Currency(
    code="BBD",
    numeric="052",
    decimals=2,
    symbol="$",
    name="Barbados Dollar",
    countries=["BARBADOS"],
)
CURRENCY["BDT"] = Currency(
    code="BDT",
    numeric="050",
    decimals=2,
    symbol="",
    name="Taka",
    countries=["BANGLADESH"],
)
CURRENCY["BGN"] = Currency(
    code="BGN",
    numeric="975",
    decimals=2,
    symbol="лв",
    name="Bulgarian Lev",
    countries=["BULGARIA"],
)
CURRENCY["BHD"] = Currency(
    code="BHD",
    numeric="048",
    decimals=3,
    symbol="",
    name="Bahraini Dinar",
    countries=["BAHRAIN"],
)
CURRENCY["BIF"] = Currency(
    code="BIF",
    numeric="108",
    decimals=0,
    symbol="",
    name="Burundi Franc",
    countries=["BURUNDI"],
)
CURRENCY["BMD"] = Currency(
    code="BMD",
    numeric="060",
    decimals=2,
    symbol="$",
    name="Bermudian Dollar",
    countries=["BERMUDA"],
)
CURRENCY["BND"] = Currency(
    code="BND",
    numeric="096",
    decimals=2,
    symbol="$",
    name="Brunei Dollar",
    countries=["BRUNEI DARUSSALAM"],
)
CURRENCY["BOB"] = Currency(
    code="BOB",
    numeric="068",
    decimals=2,
    symbol="$b",
    name="Boliviano",
    countries=["BOLIVIA, PLURINATIONAL STATE OF"],
)
CURRENCY["BOV"] = Currency(
    code="BOV",
    numeric="984",
    decimals=2,
    symbol="",
    name="Mvdol",
    countries=["BOLIVIA, PLURINATIONAL STATE OF"],
)
CURRENCY["BRL"] = Currency(
    code="BRL",
    numeric="986",
    decimals=2,
    symbol="R$",
    name="Brazilian Real",
    countries=["BRAZIL"],
)
CURRENCY["BSD"] = Currency(
    code="BSD",
    numeric="044",
    decimals=2,
    symbol="$",
    name="Bahamian Dollar",
    countries=["BAHAMAS"],
)
CURRENCY["BTN"] = Currency(
    code="BTN",
    numeric="064",
    decimals=2,
    symbol="",
    name="Ngultrum",
    countries=["BHUTAN"],
)
CURRENCY["BWP"] = Currency(
    code="BWP",
    numeric="072",
    decimals=2,
    symbol="P",
    name="Pula",
    countries=["BOTSWANA"],
)
CURRENCY["BYR"] = Currency(
    code="BYR",
    numeric="974",
    decimals=0,
    symbol="p.",
    name="Belarussian Ruble",
    countries=["BELARUS"],
)
CURRENCY["BZD"] = Currency(
    code="BZD",
    numeric="084",
    decimals=2,
    symbol="BZ$",
    name="Belize Dollar",
    countries=["BELIZE"],
)
CURRENCY["CAD"] = Currency(
    code="CAD",
    numeric="124",
    decimals=2,
    symbol="$",
    name="Canadian Dollar",
    countries=["CANADA"],
)
CURRENCY["CDF"] = Currency(
    code="CDF",
    numeric="976",
    decimals=2,
    symbol="",
    name="Congolese Franc",
    countries=["CONGO, THE DEMOCRATIC REPUBLIC OF"],
)
CURRENCY["CHE"] = Currency(
    code="CHE",
    numeric="947",
    decimals=2,
    symbol="",
    name="WIR Euro",
    countries=["SWITZERLAND"],
)
CURRENCY["CHF"] = Currency(
    code="CHF",
    numeric="756",
    decimals=2,
    symbol="Fr.",
    name="Swiss Franc",
    countries=["LIECHTENSTEIN", "SWITZERLAND"],
)
CURRENCY["CHW"] = Currency(
    code="CHW",
    numeric="948",
    decimals=2,
    symbol="",
    name="WIR Franc",
    countries=["SWITZERLAND"],
)
CURRENCY["CLF"] = Currency(
    code="CLF",
    numeric="990",
    decimals=0,
    symbol="",
    name="Unidades de fomento",
    countries=["CHILE"],
)
CURRENCY["CLP"] = Currency(
    code="CLP",
    numeric="152",
    decimals=0,
    symbol="$",
    name="Chilean Peso",
    countries=["CHILE"],
)
CURRENCY["CNY"] = Currency(
    code="CNY",
    numeric="156",
    decimals=2,
    symbol="¥",
    name="Yuan Renminbi",
    countries=["CHINA"],
)
CURRENCY["COP"] = Currency(
    code="COP",
    numeric="170",
    decimals=2,
    symbol="$",
    name="Colombian Peso",
    countries=["COLOMBIA"],
)
CURRENCY["COU"] = Currency(
    code="COU",
    numeric="970",
    decimals=2,
    symbol="",
    name="Unidad de Valor Real",
    countries=["COLOMBIA"],
)
CURRENCY["CRC"] = Currency(
    code="CRC",
    numeric="188",
    decimals=2,
    symbol="₡",
    name="Costa Rican Colon",
    countries=["COSTA RICA"],
)
CURRENCY["CUC"] = Currency(
    code="CUC",
    numeric="931",
    decimals=2,
    symbol="",
    name="Peso Convertible",
    countries=["CUBA"],
)
CURRENCY["CUP"] = Currency(
    code="CUP",
    numeric="192",
    decimals=2,
    symbol="₱",
    name="Cuban Peso",
    countries=["CUBA"],
)
CURRENCY["CVE"] = Currency(
    code="CVE",
    numeric="132",
    decimals=2,
    symbol="",
    name="Cape Verde Escudo",
    countries=["CAPE VERDE"],
)
CURRENCY["CZK"] = Currency(
    code="CZK",
    numeric="203",
    decimals=2,
    symbol="Kč",
    name="Czech Koruna",
    countries=["CZECH REPUBLIC"],
)
CURRENCY["DJF"] = Currency(
    code="DJF",
    numeric="262",
    decimals=0,
    symbol="",
    name="Djibouti Franc",
    countries=["DJIBOUTI"],
)
CURRENCY["DKK"] = Currency(
    code="DKK",
    numeric="208",
    decimals=2,
    symbol="kr",
    name="Danish Krone",
    countries=["DENMARK", "FAROE ISLANDS", "GREENLAND"],
)
CURRENCY["DOP"] = Currency(
    code="DOP",
    numeric="214",
    decimals=2,
    symbol="RD$",
    name="Dominican Peso",
    countries=["DOMINICAN REPUBLIC"],
)
CURRENCY["DZD"] = Currency(
    code="DZD",
    numeric="012",
    decimals=2,
    symbol="",
    name="Algerian Dinar",
    countries=["ALGERIA"],
)
CURRENCY["EGP"] = Currency(
    code="EGP",
    numeric="818",
    decimals=2,
    symbol="£",
    name="Egyptian Pound",
    countries=["EGYPT"],
)
CURRENCY["ERN"] = Currency(
    code="ERN",
    numeric="232",
    decimals=2,
    symbol="",
    name="Nakfa",
    countries=["ERITREA"],
)
CURRENCY["ETB"] = Currency(
    code="ETB",
    numeric="230",
    decimals=2,
    symbol="",
    name="Ethiopian Birr",
    countries=["ETHIOPIA"],
)
CURRENCY["EUR"] = Currency(
    code="EUR",
    numeric="978",
    decimals=2,
    symbol="€",
    name="Euro",
    countries=[
        "\xc5LAND ISLANDS",
        "ANDORRA",
        "AUSTRIA",
        "BELGIUM",
        "CYPRUS",
        "ESTONIA",
        "EUROPEAN UNION ",
        "FINLAND",
        "FRANCE",
        "FRENCH GUIANA",
        "FRENCH SOUTHERN TERRITORIES",
        "GERMANY",
        "GREECE",
        "GUADELOUPE",
        "HOLY SEE (VATICAN CITY STATE)",
        "IRELAND",
        "ITALY",
        "LUXEMBOURG",
        "MALTA",
        "MARTINIQUE",
        "MAYOTTE",
        "MONACO",
        "MONTENEGRO",
        "NETHERLANDS",
        "PORTUGAL",
        "R\xc9UNION",
        "SAINT BARTH\xc9LEMY",
        "SAINT MARTIN (FRENCH PART)",
        "SAINT PIERRE AND MIQUELON",
        "SAN MARINO",
        "SLOVAKIA",
        "SLOVENIA",
        "SPAIN",
        "Vatican City State (HOLY SEE)",
    ],
)
CURRENCY["FJD"] = Currency(
    code="FJD",
    numeric="242",
    decimals=2,
    symbol="$",
    name="Fiji Dollar",
    countries=["FIJI"],
)
CURRENCY["FKP"] = Currency(
    code="FKP",
    numeric="238",
    decimals=2,
    symbol="£",
    name="Falkland Islands Pound",
    countries=["FALKLAND ISLANDS (MALVINAS)"],
)
CURRENCY["GBP"] = Currency(
    code="GBP",
    numeric="826",
    decimals=2,
    symbol="£",
    name="Pound Sterling",
    countries=["GUERNSEY", "ISLE OF MAN", "JERSEY", "UNITED KINGDOM"],
)
CURRENCY["GEL"] = Currency(
    code="GEL", numeric="981", decimals=2, symbol="", name="Lari", countries=["GEORGIA"]
)
CURRENCY["GHS"] = Currency(
    code="GHS",
    numeric="936",
    decimals=2,
    symbol="",
    name="Ghana Cedi",
    countries=["GHANA"],
)
CURRENCY["GIP"] = Currency(
    code="GIP",
    numeric="292",
    decimals=2,
    symbol="£",
    name="Gibraltar Pound",
    countries=["GIBRALTAR"],
)
CURRENCY["GMD"] = Currency(
    code="GMD",
    numeric="270",
    decimals=2,
    symbol="",
    name="Dalasi",
    countries=["GAMBIA"],
)
CURRENCY["GNF"] = Currency(
    code="GNF",
    numeric="324",
    decimals=0,
    symbol="",
    name="Guinea Franc",
    countries=["GUINEA"],
)
CURRENCY["GTQ"] = Currency(
    code="GTQ",
    numeric="320",
    decimals=2,
    symbol="Q",
    name="Quetzal",
    countries=["GUATEMALA"],
)
CURRENCY["GYD"] = Currency(
    code="GYD",
    numeric="328",
    decimals=2,
    symbol="$",
    name="Guyana Dollar",
    countries=["GUYANA"],
)
CURRENCY["HKD"] = Currency(
    code="HKD",
    numeric="344",
    decimals=2,
    symbol="HK$",
    name="Hong Kong Dollar",
    countries=["HONG KONG"],
)
CURRENCY["HNL"] = Currency(
    code="HNL",
    numeric="340",
    decimals=2,
    symbol="L",
    name="Lempira",
    countries=["HONDURAS"],
)
CURRENCY["HRK"] = Currency(
    code="HRK",
    numeric="191",
    decimals=2,
    symbol="kn",
    name="Croatian Kuna",
    countries=["CROATIA"],
)
CURRENCY["HTG"] = Currency(
    code="HTG", numeric="332", decimals=2, symbol="", name="Gourde", countries=["HAITI"]
)
CURRENCY["HUF"] = Currency(
    code="HUF",
    numeric="348",
    decimals=2,
    symbol="Ft",
    name="Forint",
    countries=["HUNGARY"],
)
CURRENCY["IDR"] = Currency(
    code="IDR",
    numeric="360",
    decimals=2,
    symbol="Rp",
    name="Rupiah",
    countries=["INDONESIA"],
)
CURRENCY["ILS"] = Currency(
    code="ILS",
    numeric="376",
    decimals=2,
    symbol="₪",
    name="New Israeli Sheqel",
    countries=["ISRAEL"],
)
CURRENCY["INR"] = Currency(
    code="INR",
    numeric="356",
    decimals=2,
    symbol="",
    name="Indian Rupee",
    countries=["BHUTAN", "INDIA"],
)
CURRENCY["IQD"] = Currency(
    code="IQD",
    numeric="368",
    decimals=3,
    symbol="",
    name="Iraqi Dinar",
    countries=["IRAQ"],
)
CURRENCY["IRR"] = Currency(
    code="IRR",
    numeric="364",
    decimals=2,
    symbol="﷼",
    name="Iranian Rial",
    countries=["IRAN, ISLAMIC REPUBLIC OF"],
)
CURRENCY["ISK"] = Currency(
    code="ISK",
    numeric="352",
    decimals=0,
    symbol="kr",
    name="Iceland Krona",
    countries=["ICELAND"],
)
CURRENCY["JMD"] = Currency(
    code="JMD",
    numeric="388",
    decimals=2,
    symbol="J$",
    name="Jamaican Dollar",
    countries=["JAMAICA"],
)
CURRENCY["JOD"] = Currency(
    code="JOD",
    numeric="400",
    decimals=3,
    symbol="",
    name="Jordanian Dinar",
    countries=["JORDAN"],
)
CURRENCY["JPY"] = Currency(
    code="JPY", numeric="392", decimals=0, symbol="¥", name="Yen", countries=["JAPAN"]
)
CURRENCY["KES"] = Currency(
    code="KES",
    numeric="404",
    decimals=2,
    symbol="",
    name="Kenyan Shilling",
    countries=["KENYA"],
)
CURRENCY["KGS"] = Currency(
    code="KGS",
    numeric="417",
    decimals=2,
    symbol="лв",
    name="Som",
    countries=["KYRGYZSTAN"],
)
CURRENCY["KHR"] = Currency(
    code="KHR",
    numeric="116",
    decimals=2,
    symbol="៛",
    name="Riel",
    countries=["CAMBODIA"],
)
CURRENCY["KMF"] = Currency(
    code="KMF",
    numeric="174",
    decimals=0,
    symbol="",
    name="Comoro Franc",
    countries=["COMOROS"],
)
CURRENCY["KPW"] = Currency(
    code="KPW",
    numeric="408",
    decimals=2,
    symbol="₩",
    name="North Korean Won",
    countries=["KOREA, DEMOCRATIC PEOPLE\u2019S REPUBLIC OF"],
)
CURRENCY["KRW"] = Currency(
    code="KRW",
    numeric="410",
    decimals=0,
    symbol="₩",
    name="Won",
    countries=["KOREA, REPUBLIC OF"],
)
CURRENCY["KWD"] = Currency(
    code="KWD",
    numeric="414",
    decimals=3,
    symbol="",
    name="Kuwaiti Dinar",
    countries=["KUWAIT"],
)
CURRENCY["KYD"] = Currency(
    code="KYD",
    numeric="136",
    decimals=2,
    symbol="$",
    name="Cayman Islands Dollar",
    countries=["CAYMAN ISLANDS"],
)
CURRENCY["KZT"] = Currency(
    code="KZT",
    numeric="398",
    decimals=2,
    symbol="лв",
    name="Tenge",
    countries=["KAZAKHSTAN"],
)
CURRENCY["LAK"] = Currency(
    code="LAK",
    numeric="418",
    decimals=2,
    symbol="₭",
    name="Kip",
    countries=["LAO PEOPLE\u2019S DEMOCRATIC REPUBLIC"],
)
CURRENCY["LBP"] = Currency(
    code="LBP",
    numeric="422",
    decimals=2,
    symbol="£",
    name="Lebanese Pound",
    countries=["LEBANON"],
)
CURRENCY["LKR"] = Currency(
    code="LKR",
    numeric="144",
    decimals=2,
    symbol="₨",
    name="Sri Lanka Rupee",
    countries=["SRI LANKA"],
)
CURRENCY["LRD"] = Currency(
    code="LRD",
    numeric="430",
    decimals=2,
    symbol="$",
    name="Liberian Dollar",
    countries=["LIBERIA"],
)
CURRENCY["LSL"] = Currency(
    code="LSL", numeric="426", decimals=2, symbol="", name="Loti", countries=["LESOTHO"]
)
CURRENCY["LTL"] = Currency(
    code="LTL",
    numeric="440",
    decimals=2,
    symbol="Lt",
    name="Lithuanian Litas",
    countries=["LITHUANIA"],
)
CURRENCY["LVL"] = Currency(
    code="LVL",
    numeric="428",
    decimals=2,
    symbol="Ls",
    name="Latvian Lats",
    countries=["LATVIA"],
)
CURRENCY["LYD"] = Currency(
    code="LYD",
    numeric="434",
    decimals=3,
    symbol="",
    name="Libyan Dinar",
    countries=["LIBYA"],
)
CURRENCY["MAD"] = Currency(
    code="MAD",
    numeric="504",
    decimals=2,
    symbol="",
    name="Moroccan Dirham",
    countries=["MOROCCO", "WESTERN SAHARA"],
)
CURRENCY["MDL"] = Currency(
    code="MDL",
    numeric="498",
    decimals=2,
    symbol="",
    name="Moldovan Leu",
    countries=["MOLDOVA, REPUBLIC OF"],
)
CURRENCY["MGA"] = Currency(
    code="MGA",
    numeric="969",
    decimals=2,
    symbol="",
    name="Malagasy Ariary",
    countries=["MADAGASCAR"],
)
CURRENCY["MKD"] = Currency(
    code="MKD",
    numeric="807",
    decimals=2,
    symbol="ден",
    name="Denar",
    countries=["MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF"],
)
CURRENCY["MMK"] = Currency(
    code="MMK",
    numeric="104",
    decimals=2,
    symbol="K",
    name="Kyat",
    countries=["MYANMAR"],
)
CURRENCY["MNT"] = Currency(
    code="MNT",
    numeric="496",
    decimals=2,
    symbol="₮",
    name="Tugrik",
    countries=["MONGOLIA"],
)
CURRENCY["MOP"] = Currency(
    code="MOP", numeric="446", decimals=2, symbol="", name="Pataca", countries=["MACAO"]
)
CURRENCY["MRO"] = Currency(
    code="MRO",
    numeric="478",
    decimals=2,
    symbol="",
    name="Ouguiya",
    countries=["MAURITANIA"],
)
CURRENCY["MUR"] = Currency(
    code="MUR",
    numeric="480",
    decimals=2,
    symbol="₨",
    name="Mauritius Rupee",
    countries=["MAURITIUS"],
)
CURRENCY["MVR"] = Currency(
    code="MVR",
    numeric="462",
    decimals=2,
    symbol="",
    name="Rufiyaa",
    countries=["MALDIVES"],
)
CURRENCY["MWK"] = Currency(
    code="MWK",
    numeric="454",
    decimals=2,
    symbol="",
    name="Kwacha",
    countries=["MALAWI"],
)
CURRENCY["MXN"] = Currency(
    code="MXN",
    numeric="484",
    decimals=2,
    symbol="$",
    name="Mexican Peso",
    countries=["MEXICO"],
)
CURRENCY["MXV"] = Currency(
    code="MXV",
    numeric="979",
    decimals=2,
    symbol="",
    name="Mexican Unidad de Inversion (UDI)",
    countries=["MEXICO"],
)
CURRENCY["MYR"] = Currency(
    code="MYR",
    numeric="458",
    decimals=2,
    symbol="RM",
    name="Malaysian Ringgit",
    countries=["MALAYSIA"],
)
CURRENCY["MZN"] = Currency(
    code="MZN",
    numeric="943",
    decimals=2,
    symbol="MT",
    name="Mozambique Metical",
    countries=["MOZAMBIQUE"],
)
CURRENCY["NAD"] = Currency(
    code="NAD",
    numeric="516",
    decimals=2,
    symbol="$",
    name="Namibia Dollar",
    countries=["NAMIBIA"],
)
CURRENCY["NGN"] = Currency(
    code="NGN",
    numeric="566",
    decimals=2,
    symbol="₦",
    name="Naira",
    countries=["NIGERIA"],
)
CURRENCY["NIO"] = Currency(
    code="NIO",
    numeric="558",
    decimals=2,
    symbol="C$",
    name="Cordoba Oro",
    countries=["NICARAGUA"],
)
CURRENCY["NOK"] = Currency(
    code="NOK",
    numeric="578",
    decimals=2,
    symbol="kr",
    name="Norwegian Krone",
    countries=["BOUVET ISLAND", "NORWAY", "SVALBARD AND JAN MAYEN"],
)
CURRENCY["NPR"] = Currency(
    code="NPR",
    numeric="524",
    decimals=2,
    symbol="₨",
    name="Nepalese Rupee",
    countries=["NEPAL"],
)
CURRENCY["NZD"] = Currency(
    code="NZD",
    numeric="554",
    decimals=2,
    symbol="$",
    name="New Zealand Dollar",
    countries=["COOK ISLANDS", "NEW ZEALAND", "NIUE", "PITCAIRN", "TOKELAU"],
)
CURRENCY["OMR"] = Currency(
    code="OMR",
    numeric="512",
    decimals=3,
    symbol="﷼",
    name="Rial Omani",
    countries=["OMAN"],
)
CURRENCY["PAB"] = Currency(
    code="PAB",
    numeric="590",
    decimals=2,
    symbol="B/.",
    name="Balboa",
    countries=["PANAMA"],
)
CURRENCY["PEN"] = Currency(
    code="PEN",
    numeric="604",
    decimals=2,
    symbol="S/.",
    name="Nuevo Sol",
    countries=["PERU"],
)
CURRENCY["PGK"] = Currency(
    code="PGK",
    numeric="598",
    decimals=2,
    symbol="",
    name="Kina",
    countries=["PAPUA NEW GUINEA"],
)
CURRENCY["PHP"] = Currency(
    code="PHP",
    numeric="608",
    decimals=2,
    symbol="₱",
    name="Philippine Peso",
    countries=["PHILIPPINES"],
)
CURRENCY["PKR"] = Currency(
    code="PKR",
    numeric="586",
    decimals=2,
    symbol="₨",
    name="Pakistan Rupee",
    countries=["PAKISTAN"],
)
CURRENCY["PLN"] = Currency(
    code="PLN",
    numeric="985",
    decimals=2,
    symbol="zł",
    name="Zloty",
    countries=["POLAND"],
)
CURRENCY["PYG"] = Currency(
    code="PYG",
    numeric="600",
    decimals=0,
    symbol="Gs",
    name="Guarani",
    countries=["PARAGUAY"],
)
CURRENCY["QAR"] = Currency(
    code="QAR",
    numeric="634",
    decimals=2,
    symbol="﷼",
    name="Qatari Rial",
    countries=["QATAR"],
)
CURRENCY["RON"] = Currency(
    code="RON",
    numeric="946",
    decimals=2,
    symbol="lei",
    name="New Romanian Leu",
    countries=["ROMANIA"],
)
CURRENCY["RSD"] = Currency(
    code="RSD",
    numeric="941",
    decimals=2,
    symbol="Дин.",
    name="Serbian Dinar",
    countries=["SERBIA "],
)
CURRENCY["RUB"] = Currency(
    code="RUB",
    numeric="643",
    decimals=2,
    symbol="руб",
    name="Russian Ruble",
    countries=["RUSSIAN FEDERATION"],
)
CURRENCY["RWF"] = Currency(
    code="RWF",
    numeric="646",
    decimals=0,
    symbol="",
    name="Rwanda Franc",
    countries=["RWANDA"],
)
CURRENCY["SAR"] = Currency(
    code="SAR",
    numeric="682",
    decimals=2,
    symbol="﷼",
    name="Saudi Riyal",
    countries=["SAUDI ARABIA"],
)
CURRENCY["SBD"] = Currency(
    code="SBD",
    numeric="090",
    decimals=2,
    symbol="$",
    name="Solomon Islands Dollar",
    countries=["SOLOMON ISLANDS"],
)
CURRENCY["SCR"] = Currency(
    code="SCR",
    numeric="690",
    decimals=2,
    symbol="₨",
    name="Seychelles Rupee",
    countries=["SEYCHELLES"],
)
CURRENCY["SDG"] = Currency(
    code="SDG",
    numeric="938",
    decimals=2,
    symbol="",
    name="Sudanese Pound",
    countries=["SUDAN"],
)
CURRENCY["SEK"] = Currency(
    code="SEK",
    numeric="752",
    decimals=2,
    symbol="kr",
    name="Swedish Krona",
    countries=["SWEDEN"],
)
CURRENCY["SGD"] = Currency(
    code="SGD",
    numeric="702",
    decimals=2,
    symbol="$",
    name="Singapore Dollar",
    countries=["SINGAPORE"],
)
CURRENCY["SHP"] = Currency(
    code="SHP",
    numeric="654",
    decimals=2,
    symbol="£",
    name="Saint Helena Pound",
    countries=["SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA"],
)
CURRENCY["SLL"] = Currency(
    code="SLL",
    numeric="694",
    decimals=2,
    symbol="",
    name="Leone",
    countries=["SIERRA LEONE"],
)
CURRENCY["SOS"] = Currency(
    code="SOS",
    numeric="706",
    decimals=2,
    symbol="S",
    name="Somali Shilling",
    countries=["SOMALIA"],
)
CURRENCY["SRD"] = Currency(
    code="SRD",
    numeric="968",
    decimals=2,
    symbol="$",
    name="Surinam Dollar",
    countries=["SURINAME"],
)
CURRENCY["SSP"] = Currency(
    code="SSP",
    numeric="728",
    decimals=2,
    symbol="",
    name="South Sudanese Pound",
    countries=["SOUTH SUDAN"],
)
CURRENCY["STD"] = Currency(
    code="STD",
    numeric="678",
    decimals=2,
    symbol="",
    name="Dobra",
    countries=["SAO TOME AND PRINCIPE"],
)
CURRENCY["SVC"] = Currency(
    code="SVC",
    numeric="222",
    decimals=2,
    symbol="$",
    name="El Salvador Colon",
    countries=["EL SALVADOR"],
)
CURRENCY["SYP"] = Currency(
    code="SYP",
    numeric="760",
    decimals=2,
    symbol="£",
    name="Syrian Pound",
    countries=["SYRIAN ARAB REPUBLIC"],
)
CURRENCY["SZL"] = Currency(
    code="SZL",
    numeric="748",
    decimals=2,
    symbol="",
    name="Lilangeni",
    countries=["SWAZILAND"],
)
CURRENCY["THB"] = Currency(
    code="THB",
    numeric="764",
    decimals=2,
    symbol="฿",
    name="Baht",
    countries=["THAILAND"],
)
CURRENCY["TJS"] = Currency(
    code="TJS",
    numeric="972",
    decimals=2,
    symbol="",
    name="Somoni",
    countries=["TAJIKISTAN"],
)
CURRENCY["TMT"] = Currency(
    code="TMT",
    numeric="934",
    decimals=2,
    symbol="",
    name="Turkmenistan New Manat",
    countries=["TURKMENISTAN"],
)
CURRENCY["TND"] = Currency(
    code="TND",
    numeric="788",
    decimals=3,
    symbol="",
    name="Tunisian Dinar",
    countries=["TUNISIA"],
)
CURRENCY["TOP"] = Currency(
    code="TOP",
    numeric="776",
    decimals=2,
    symbol="",
    name="Pa’anga",
    countries=["TONGA"],
)
CURRENCY["TRY"] = Currency(
    code="TRY",
    numeric="949",
    decimals=2,
    symbol="TL",
    name="Turkish Lira",
    countries=["TURKEY"],
)
CURRENCY["TTD"] = Currency(
    code="TTD",
    numeric="780",
    decimals=2,
    symbol="TT$",
    name="Trinidad and Tobago Dollar",
    countries=["TRINIDAD AND TOBAGO"],
)
CURRENCY["TWD"] = Currency(
    code="TWD",
    numeric="901",
    decimals=2,
    symbol="NT$",
    name="New Taiwan Dollar",
    countries=["TAIWAN, PROVINCE OF CHINA"],
)
CURRENCY["TZS"] = Currency(
    code="TZS",
    numeric="834",
    decimals=2,
    symbol="",
    name="Tanzanian Shilling",
    countries=["TANZANIA, UNITED REPUBLIC OF"],
)
CURRENCY["UAH"] = Currency(
    code="UAH",
    numeric="980",
    decimals=2,
    symbol="₴",
    name="Hryvnia",
    countries=["UKRAINE"],
)
CURRENCY["UGX"] = Currency(
    code="UGX",
    numeric="800",
    decimals=2,
    symbol="",
    name="Uganda Shilling",
    countries=["UGANDA"],
)
CURRENCY["USD"] = Currency(
    code="USD",
    numeric="840",
    decimals=2,
    symbol="$",
    name="US Dollar",
    countries=[
        "AMERICAN SAMOA",
        "BONAIRE, SINT EUSTATIUS AND SABA",
        "BRITISH INDIAN OCEAN TERRITORY",
        "ECUADOR",
        "EL SALVADOR",
        "GUAM",
        "HAITI",
        "MARSHALL ISLANDS",
        "MICRONESIA, FEDERATED STATES OF",
        "NORTHERN MARIANA ISLANDS",
        "PALAU",
        "PANAMA",
        "PUERTO RICO",
        "TIMOR-LESTE",
        "TURKS AND CAICOS ISLANDS",
        "UNITED STATES",
        "UNITED STATES MINOR OUTLYING ISLANDS",
        "VIRGIN ISLANDS (BRITISH)",
        "VIRGIN ISLANDS (US)",
    ],
)
CURRENCY["USN"] = Currency(
    code="USN",
    numeric="997",
    decimals=2,
    symbol="$",
    name="US Dollar (Next day)",
    countries=["UNITED STATES"],
)
CURRENCY["USS"] = Currency(
    code="USS",
    numeric="998",
    decimals=2,
    symbol="$",
    name="US Dollar (Same day)",
    countries=["UNITED STATES"],
)
CURRENCY["UYI"] = Currency(
    code="UYI",
    numeric="940",
    decimals=0,
    symbol="",
    name="Uruguay Peso en Unidades Indexadas (URUIURUI)",
    countries=["URUGUAY"],
)
CURRENCY["UYU"] = Currency(
    code="UYU",
    numeric="858",
    decimals=2,
    symbol="$U",
    name="Peso Uruguayo",
    countries=["URUGUAY"],
)
CURRENCY["UZS"] = Currency(
    code="UZS",
    numeric="860",
    decimals=2,
    symbol="лв",
    name="Uzbekistan Sum",
    countries=["UZBEKISTAN"],
)
CURRENCY["VEF"] = Currency(
    code="VEF",
    numeric="937",
    decimals=2,
    symbol="Bs",
    name="Bolivar Fuerte",
    countries=["VENEZUELA, BOLIVARIAN REPUBLIC OF"],
)
CURRENCY["VND"] = Currency(
    code="VND",
    numeric="704",
    decimals=0,
    symbol="₫",
    name="Dong",
    countries=["VIET NAM"],
)
CURRENCY["VUV"] = Currency(
    code="VUV", numeric="548", decimals=0, symbol="", name="Vatu", countries=["VANUATU"]
)
CURRENCY["WST"] = Currency(
    code="WST", numeric="882", decimals=2, symbol="", name="Tala", countries=["SAMOA"]
)
CURRENCY["XAF"] = Currency(
    code="XAF",
    numeric="950",
    decimals=0,
    symbol="",
    name="CFA Franc BEAC",
    countries=[
        "CAMEROON",
        "CENTRAL AFRICAN REPUBLIC",
        "CHAD",
        "CONGO",
        "EQUATORIAL GUINEA",
        "GABON",
    ],
)
CURRENCY["XAG"] = Currency(
    code="XAG",
    numeric="961",
    decimals=0,
    symbol="",
    name="Silver",
    countries=["ZZ11_Silver"],
)
CURRENCY["XAU"] = Currency(
    code="XAU",
    numeric="959",
    decimals=0,
    symbol="",
    name="Gold",
    countries=["ZZ08_Gold"],
)
CURRENCY["XBA"] = Currency(
    code="XBA",
    numeric="955",
    decimals=0,
    symbol="",
    name="Bond Markets Unit European Composite Unit (EURCO)",
    countries=["ZZ01_Bond Markets Unit European_EURCO"],
)
CURRENCY["XBB"] = Currency(
    code="XBB",
    numeric="956",
    decimals=0,
    symbol="",
    name="Bond Markets Unit European Monetary Unit (E.M.U.-6)",
    countries=["ZZ02_Bond Markets Unit European_EMU-6"],
)
CURRENCY["XBC"] = Currency(
    code="XBC",
    numeric="957",
    decimals=0,
    symbol="",
    name="Bond Markets Unit European Unit of Account 9 (E.U.A.-9)",
    countries=["ZZ03_Bond Markets Unit European_EUA-9"],
)
CURRENCY["XBD"] = Currency(
    code="XBD",
    numeric="958",
    decimals=0,
    symbol="",
    name="Bond Markets Unit European Unit of Account 17 (E.U.A.-17)",
    countries=["ZZ04_Bond Markets Unit European_EUA-17"],
)
CURRENCY["XCD"] = Currency(
    code="XCD",
    numeric="951",
    decimals=2,
    symbol="$",
    name="East Caribbean Dollar",
    countries=[
        "ANGUILLA",
        "ANTIGUA AND BARBUDA",
        "DOMINICA",
        "GRENADA",
        "MONTSERRAT",
        "SAINT KITTS AND NEVIS",
        "SAINT LUCIA",
        "SAINT VINCENT AND THE GRENADINES",
    ],
)
CURRENCY["XDR"] = Currency(
    code="XDR",
    numeric="960",
    decimals=0,
    symbol="",
    name="SDR (Special Drawing Right)",
    countries=["INTERNATIONAL MONETARY FUND (IMF)\xa0"],
)
CURRENCY["XFU"] = Currency(
    code="XFU",
    numeric="Nil",
    decimals=0,
    symbol="",
    name="UIC-Franc",
    countries=["ZZ05_UIC-Franc"],
)
CURRENCY["XOF"] = Currency(
    code="XOF",
    numeric="952",
    decimals=0,
    symbol="",
    name="CFA Franc BCEAO",
    countries=[
        "BENIN",
        "BURKINA FASO",
        "C\xd4TE D'IVOIRE",
        "GUINEA-BISSAU",
        "MALI",
        "NIGER",
        "SENEGAL",
        "TOGO",
    ],
)
CURRENCY["XPD"] = Currency(
    code="XPD",
    numeric="964",
    decimals=0,
    symbol="",
    name="Palladium",
    countries=["ZZ09_Palladium"],
)
CURRENCY["XPF"] = Currency(
    code="XPF",
    numeric="953",
    decimals=0,
    symbol="",
    name="CFP Franc",
    countries=["FRENCH POLYNESIA", "NEW CALEDONIA", "WALLIS AND FUTUNA"],
)
CURRENCY["XPT"] = Currency(
    code="XPT",
    numeric="962",
    decimals=0,
    symbol="",
    name="Platinum",
    countries=["ZZ10_Platinum"],
)
CURRENCY["XSU"] = Currency(
    code="XSU",
    numeric="994",
    decimals=0,
    symbol="",
    name="Sucre",
    countries=['SISTEMA UNITARIO DE COMPENSACION REGIONAL DE PAGOS "SUCRE" '],
)
CURRENCY["XTS"] = Currency(
    code="XTS",
    numeric="963",
    decimals=0,
    symbol="",
    name="Codes specifically reserved for testing purposes",
    countries=["ZZ06_Testing_Code"],
)
CURRENCY["XUA"] = Currency(
    code="XUA",
    numeric="965",
    decimals=0,
    symbol="",
    name="ADB Unit of Account",
    countries=["MEMBER COUNTRIES OF THE AFRICAN DEVELOPMENT BANK GROUP"],
)
CURRENCY["XXX"] = Currency(
    code="XXX",
    numeric="999",
    decimals=0,
    symbol="",
    name="The codes assigned for transactions where no currency is involved",
    countries=["ZZ07_No_Currency"],
)
CURRENCY["YER"] = Currency(
    code="YER",
    numeric="886",
    decimals=2,
    symbol="﷼",
    name="Yemeni Rial",
    countries=["YEMEN"],
)
CURRENCY["ZAR"] = Currency(
    code="ZAR",
    numeric="710",
    decimals=2,
    symbol="R",
    name="Rand",
    countries=["LESOTHO", "NAMIBIA", "SOUTH AFRICA"],
)
CURRENCY["ZMK"] = Currency(
    code="ZMK",
    numeric="894",
    decimals=2,
    symbol="",
    name="Zambian Kwacha",
    countries=["ZAMBIA"],
)
CURRENCY["ZWL"] = Currency(
    code="ZWL",
    numeric="932",
    decimals=2,
    symbol="",
    name="Zimbabwe Dollar",
    countries=["ZIMBABWE"],
)
