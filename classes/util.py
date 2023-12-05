import math
import random
import pygame
import numpy as np
from enum import Enum
from typing import List, Tuple, Union, TypeVar, Callable


class Cell(Enum):
    EMPTY = 0
    FULL = 1


class Action(Enum):
    NONE = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


Vector2 = Tuple[int, int]
Vector3 = Tuple[int, int, int]

T = TypeVar('T')
Array2D = List[List[T]]

Event = Union[pygame.event.EventType, pygame.event.Event]
Surface = pygame.Surface