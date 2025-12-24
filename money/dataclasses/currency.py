import dataclasses


@dataclasses.dataclass(frozen=True)
class Currency:
    code: str = "XXX"
    numeric: str = "999"
    name: str = ""
    symbol: str = ""
    decimals: int = 2
    countries: list[str] = dataclasses.field(default_factory=list)

    def __repr__(self) -> str:
        return self.code

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Currency):
            return bool(self.code and other.code and (self.code == other.code))
        if isinstance(other, str):
            return self.code == other
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
