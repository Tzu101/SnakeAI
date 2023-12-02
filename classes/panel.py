from classes.util import *
from classes.abstract import WindowComponent


class Panel(WindowComponent):
	BACKGROUND_COLOR = (15, 15, 15)

	def __init__(self, width: int, height: int):
		WindowComponent.__init__(self, width, height)

	def display(self):
		super().display()
