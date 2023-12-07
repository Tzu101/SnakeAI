from classes.util import *


class Controler:

    def __init__(self):
        self.action: Action = Action.NONE

    def compute_action(self, grid: Array2D[Cell], snake: List[Vector2], apple: Vector2) -> Action:
        return Action.NONE