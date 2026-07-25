from enum import Enum, auto


class States(Enum):
    START = auto()
    GAMEPLAY = auto()
    RETRY = auto()