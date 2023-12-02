from classes.util import *
from classes.game import Game
from classes.panel import Panel


class Window:
	PANEL_HEIGHT = 100
	GAME_WIDTH = 800
	GAME_HEIGHT = 800

	SCREEN_WIDTH = GAME_WIDTH
	SCREEN_HEIGHT = GAME_HEIGHT + PANEL_HEIGHT

	FPS = 60
	
	def __init__(self):
		pygame.init()

		self.panel = Panel(Window.SCREEN_WIDTH, Window.PANEL_HEIGHT)
		self.game = Game(Window.SCREEN_WIDTH, Window.GAME_HEIGHT)

		self.screen = pygame.display.set_mode((Window.SCREEN_WIDTH, Window.SCREEN_HEIGHT))
		self.clock = pygame.time.Clock()

		self.is_running = True
		self.delta_time = 0
	
	def update(self):
		for event in pygame.event.get():			
			if event.type == pygame.QUIT:
				self.is_running = False
		
		self.game.update(self.delta_time)
		
		self.delta_time = self.clock.tick(Window.FPS) / 1000

	def render(self):
		# Game
		self.game.display()
		self.screen.blit(self.game.surface, (0, 0))

		# Panel
		self.panel.display()
		self.screen.blit(self.panel.surface, (0, Window.GAME_HEIGHT))

	  # Render
		pygame.display.flip()
	
	def run(self):
		while self.is_running:
			self.update()
			self.render()
		pygame.quit()
