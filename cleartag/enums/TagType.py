from enum import Enum

class TagType(Enum):
    UNKNOWN = 1
    ID3 = 2
    FLAC = 3
    MP4 = 4

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value