import math
import random
import pygame
import numpy as np
from enum import IntEnum
from typing import List, Tuple, Union, TypeVar, Callable


class Cell(IntEnum):
    EMPTY = 0
    FULL = -1


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


Vector2 = Tuple[int, int]
Vector3 = Tuple[int, int, int]

T = TypeVar('T')
Array2D = List[List[T]]

Event = Union[pygame.event.EventType, pygame.event.Event]
Surface = pygame.Surface