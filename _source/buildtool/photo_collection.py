from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from .types import PartialDate

from .genre import PhotoGenre

from .photo_info import PhotoInfo


@dataclass(frozen=True)
class PhotoCollection:
    photos: Sequence[PhotoInfo]

    @property
    def dates(self) -> list[PartialDate]:
        return sorted({p.date for p in self.photos})

    @property
    def genres(self) -> list[PhotoGenre]:
        return sorted({g for p in self.photos for g in p.genre})

    def get_genre(self, genre: PhotoGenre) -> list[PhotoInfo]:
        return [p for p in self.photos if genre in p.genre]

    def __iter__(self) -> Iterator[PhotoInfo]:
        return iter(self.photos)
    
    def __len__(self) -> int:
        return len(self.photos)
