import random
from classes.util import *
from classes.game import Game
from classes.panel import Panel
from classes.network import Network, GeneticAlgorithm
from classes.controler import ManualControler, NeuralControler


class Window:
	PANEL_HEIGHT = 100
	GAMEPLAY_WIDTH = 800
	GAMEPLAY_HEIGHT = 800
	GAME_COLUMNS = 5
	GAME_ROWS = 5
	GAME_SPEED = 0

	GAME_WIDTH = GAMEPLAY_WIDTH // GAME_COLUMNS
	GAME_HEIGHT = GAMEPLAY_HEIGHT // GAME_ROWS

	SCREEN_WIDTH = GAMEPLAY_WIDTH
	SCREEN_HEIGHT = GAMEPLAY_HEIGHT + PANEL_HEIGHT

	@staticmethod
	def simple_network() -> Network:
		network = Network(8)
		network.layer(7, Network.initRand, Network.sigmoid)
		network.layer(6, Network.initRand, Network.sigmoid)
		network.layer(5, Network.initRand, Network.sigmoid)
		network.layer(4, Network.initRand, Network.none)
		return network
	
	def __init__(self):
		pygame.init()

		self.panel: Panel = Panel(Window.SCREEN_WIDTH, Window.PANEL_HEIGHT)

		self.population_size = Window.GAME_COLUMNS * Window.GAME_ROWS
		self.survival_size = self.population_size // 2

		self.game_timer = 0
		self.game_delay = Window.GAME_SPEED / self.population_size
		self.current_game = 0
		self.network_constructor = Window.simple_network
		self.games_over = 0

		self.networks: List[Network] = []
		self.games: List[Game] = []
		for _ in range(self.population_size):
			network = self.network_constructor()
			self.networks.append(network)
			self.games.append(Game(Window.GAME_WIDTH, Window.GAME_HEIGHT, NeuralControler(network)))

		self.screen = pygame.display.set_mode((Window.SCREEN_WIDTH, Window.SCREEN_HEIGHT))
		self.clock = pygame.time.Clock()

		self.is_running = True
		self.delta_time = 0

	def iterate_population(self):
		self.games_over = 0

		scores = []
		for game in self.games:
			scores.append((len(game.snake) - 1) * game.feeding_moves)

		agent_scores = list(zip(scores, self.networks))
		sorted_agent_scores = sorted(agent_scores, key=lambda x: x[0])
		sorted_agents = [network for _, network in sorted_agent_scores]
		surviving_agents = sorted_agents[-self.survival_size:]

		self.games = []
		self.networks = []
		for _ in range(self.population_size - self.survival_size):
			new_agent = self.network_constructor()
			self.networks.append(new_agent)

			parent1 = surviving_agents[random.randint(0, self.survival_size-1)]
			parent2 = surviving_agents[random.randint(0, self.survival_size-1)]

			GeneticAlgorithm.crossover(new_agent, parent1, parent2)    
			GeneticAlgorithm.mutation(new_agent, 0.1)

			new_game = Game(Window.GAME_WIDTH, Window.GAME_HEIGHT, NeuralControler(new_agent))
			self.games.append(new_game)

		for surviving_agent in surviving_agents:
			self.networks.append(surviving_agent)

			surviving_game = Game(Window.GAME_WIDTH, Window.GAME_HEIGHT, NeuralControler(surviving_agent))
			self.games.append(surviving_game)
	
	def run_games(self):
		self.game_timer += self.delta_time
		if self.game_timer >= self.game_delay:
			self.game_timer -= self.game_delay

			if not self.games[self.current_game].is_over:
				self.games_over += int(self.games[self.current_game].update())

				if self.games_over >= self.population_size:
					self.current_step = 0
					self.iterate_population()

			self.current_game += 1
			if self.current_game >= self.population_size:
				self.current_game = 0
	
	def update(self):
		for event in pygame.event.get():			
			if event.type == pygame.QUIT:
				self.is_running = False
		
		self.run_games()

		self.delta_time = self.clock.tick() / 1000

	def render(self):
		# Game
		for game_index in range(self.population_size):
			game = self.games[game_index]
			game.display()
			self.screen.blit(game.surface, (game_index % Window.GAME_ROWS * Window.GAME_WIDTH, game_index // Window.GAME_ROWS * Window.GAME_HEIGHT))

		# Panel
		self.panel.display()
		self.screen.blit(self.panel.surface, (0, Window.GAMEPLAY_HEIGHT))

	  # Render
		pygame.display.flip()
	
	def run(self):
		while self.is_running:
			self.update()
			self.render()
		pygame.quit()
