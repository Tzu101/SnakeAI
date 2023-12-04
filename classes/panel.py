from classes.util import *
from classes.abstract import WindowComponent


class Panel(WindowComponent):
	BACKGROUND_COLOR = (15, 15, 15)

	def __init__(self, width: int, height: int):
		WindowComponent.__init__(self, width, height)

		self.font = pygame.font.Font(None, 36)

	def display(self):
		super().display()

		# Render text
		text = self.font.render("Press SPACE to pause rendering and accelerate learning!", True, (0, 0, 0))

		# Get the rectangle of the text surface
		text_rect = text.get_rect()

		# Draw the text on the screen
		self.surface.blit(text, text_rect.topleft)
