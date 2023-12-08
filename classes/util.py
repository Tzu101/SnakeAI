import math
import random
import pygame
import numpy as np
from enum import IntEnum, Enum
from typing import List, Tuple, Union, TypeVar, Callable


class Mode(Enum):
    PLAY = 0
    SIMULATE = 1
    ARCHIVE = 2


class View(Enum):
    BEST=0
    ALL=1


class Cell(IntEnum):
    EMPTY = 0
    FULL = -1


class Key(Enum):
    UP = "Up"
    LEFT = "Left"
    DOWN = "Down"
    RIGHT = "Right"


class Action(IntEnum):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


def random_round(value: float):
    value_int = int(value)
    value_float = value - value_int
    return value_int + int(np.random.rand() < value_float)

T = TypeVar('T')
Array2D = List[List[T]]

Vector2 = Tuple[T, T]
Vector3 = Tuple[T, T, T]
Vector4 = Tuple[T, T, T, T]

Event = Union[pygame.event.EventType, pygame.event.Event]
Surface = pygame.Surface
