from classes.util import *


class WindowComponent:
	BACKGROUND_COLOR = (0, 0, 0)

	def __init__(self, width: int, height: int):
		self.width = width
		self.height = height

		self.surface: Surface = pygame.Surface((width, height))

	def display(self):
		self.surface.fill(self.BACKGROUND_COLOR)


class Controler:

    def __init__(self):
        self.action: Action = Action.NONE

    def compute_action(self, grid: Array2D[bool], snake: List[Vector2], apple: Vector2) -> Action:
        return Action.NONE