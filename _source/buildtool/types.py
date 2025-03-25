from dataclasses import dataclass
import datetime as dt
from decimal import Decimal
from typing import Annotated, NewType, TypeVar

from annotated_types import Gt
import pydantic


N = TypeVar('N')


@dataclass(frozen=True, order=True)
class PartialDate:
    year: int | None
    month: int | None
    day: int | None

    def __post_init__(self) -> None:
        if self.year is not None:
            if not 0 <= self.year <= 9999:
                raise ValueError('year must be in the range [0, 9999]')
        if self.month is not None:
            if self.year is None:
                raise ValueError('year must be specified with month')
            if not 1 <= self.month <= 12:
                raise ValueError('month must be in the range [1, 12]')
        if self.day is not None:
            if self.year is None:
                raise ValueError('year must be specified with day')
            if self.month is None:
                raise ValueError('month must be specified with day')
            # Validate full date
            _ = dt.date(self.year, self.month, self.day)

    @classmethod
    def from_str(cls, s: str):
        # YYYYMMDD
        if len(s) not in (0, 4, 6, 8):
            raise ValueError(f'Invalid {cls.__name__} format')
        year = int(s[:4]) if len(s) > 0 else None
        month = int(s[4:6]) if len(s) > 4 else None
        day = int(s[6:8]) if len(s) > 6 else None
        return cls(year=year, month=month, day=day)

    @classmethod
    def from_date(cls, date: dt.date):
        return cls(year=date.year, month=date.month, day=date.day)

    def __str__(self) -> str:
        s = ''
        if self.year is not None:
            assert 0 <= self.year <= 9999
            s = str(self.year).zfill(4)
        if self.month is not None:
            assert 1 <= self.month <= 12
            s += str(self.month).zfill(2)
        if self.day is not None:
            assert 1 <= self.day <= 31
            s += str(self.day).zfill(2)
        return s


NonEmptyStr = Annotated[str, pydantic.StringConstraints(strict=True, min_length=1)]

PhotoUniqueId = NewType('PhotoUniqueId', str)
FocalLength = Annotated[NewType('FocalLength', int), Gt(0)] # In millimetres
Aperture = Annotated[NewType('Aperture', Decimal), Gt(0)]
ExposureTime = Annotated[NewType('ExposureTime', Decimal), Gt(0)]
ISO = Annotated[NewType('ISO', int), Gt(0)]

# Use with custom numeric types to allow them to work with Pydantic.
CoerceNumber = Annotated[N, pydantic.BeforeValidator(lambda v: v if isinstance(v, (int, float, complex, Decimal, str)) else float(v))]
