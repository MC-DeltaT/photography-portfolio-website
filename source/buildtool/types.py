from collections.abc import Iterator
from dataclasses import dataclass
import datetime as dt
from decimal import Decimal
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Annotated, NewType, TypeVar

from annotated_types import Gt
import pydantic


N = TypeVar('N')


class PhotoGenre(StrEnum):
    ABSTRACT = 'abstract'
    ASTROPHOTOGRAPHY = 'astrophotography'
    COSTUME = 'costume'
    EVENT = 'event'
    LANDSCAPE = 'landscape'
    MACRO = 'macro'
    MONOCHROME = 'monochrome'
    NATURE = 'nature'
    PEOPLE = 'people'
    PLANT = 'plant'
    STILL_LIFE = 'still-life'
    URBAN = 'urban'
    WILDLIFE = 'wildlife'


class URLPath(PurePosixPath):
    def __init__(self, *args, **kwargs) -> None:    # type: ignore
        super().__init__(*args, **kwargs)   # type: ignore
        if not self.is_absolute():
            raise ValueError('path must have a root')

    @property
    def fs_path(self) -> Path:
        return Path(*self.parts[1:])


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

    def to_str(self, separator: str = '') -> str:
        parts: list[str] = []
        if self.year is not None:
            assert 0 <= self.year <= 9999
            parts.append(str(self.year).zfill(4))
            if self.month is not None:
                assert 1 <= self.month <= 12
                parts.append(str(self.month).zfill(2))
                if self.day is not None:
                    assert 1 <= self.day <= 31
                    parts.append(str(self.day).zfill(2))
        s = separator.join(parts)
        return s

    def __bool__(self) -> bool:
        return self.year is not None or self.month is not None or self.day is not None


NonEmptyStr = Annotated[str, pydantic.StringConstraints(strict=True, min_length=1)]

PhotoID = NewType('PhotoID', str)
"""Uniquely identifies a photo within the set of all photos.
    Includes the file extension.
    Separate from ImageID."""

FocalLength = Annotated[NewType('FocalLength', int), Gt(0)]
"""In millimetres"""

Aperture = Annotated[NewType('Aperture', Decimal), Gt(0)]

ExposureTime = Annotated[NewType('ExposureTime', Decimal), Gt(0)]

ISO = Annotated[NewType('ISO', int), Gt(0)]

CoerceNumber = Annotated[N, pydantic.BeforeValidator(lambda v: v if isinstance(v, (int, float, complex, Decimal, str)) else float(v))]
"""Use with custom numeric types to allow them to work with Pydantic."""

Size = NewType('Size', tuple[int, int])
"""(width, height)"""

ImageID = NewType('ImageID', str)
"""Path to the image relative to the image asset directory. E.g. photo/xyz.jpg"""


@dataclass(frozen=True)
class ImageSrcSet:
    @dataclass(frozen=True)
    class Entry:
        url: URLPath
        descriptor: str

    entries: tuple[Entry, ...]
    default_index: int

    def __post_init__(self) -> None:
        if self.default_index >= len(self.entries):
            raise ValueError('Invalid default_index')

    @property
    def default(self) -> Entry:
        return self.entries[self.default_index]

    def __iter__(self) -> Iterator[Entry]:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self)
