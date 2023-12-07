import sys
from classes.util import *
from classes.game import Game
from classes.network import NeuralNetwork, GeneticAlgorithm
from classes.controler import ManualControler, NeuralControler


class Window:

	class Text:
		COLOR = (220, 220, 200)
		ANTI_ALIAS = True

		def change_text(self, text: str):
			self.text = self.font.render(text, Window.Text.ANTI_ALIAS, Window.Text.COLOR)

		def __init__(self, font, text: str, position: Vector2):
			self.font = font
			self.change_text(text)
			self.position = position
		
		def display(self, screen: Surface):
			screen.blit(self.text, self.position)
	
	class Button:
		COLOR = (60, 60, 60)
		HIGHLIGHT_COLOR = (80, 80, 80)

		def __init__(self, position: Vector2, size: Vector2, font, text, onclick: Callable):
			self.position = position
			self.size = size

			self.hitbox: Vector4 = (Window.SIMULATION_WIDTH + position[0], position[1], Window.SIMULATION_WIDTH + position[0] + size[0], position[1] + size[1])
			self.onclick = onclick

			self.text = Window.Text(font, text, position)
			self.text.position = (
				self.position[0] + self.size[0] // 2 - self.text.text.get_size()[0] // 2,
				self.position[1] + self.size[1] // 2 - self.text.text.get_size()[1] // 2
			)

			self.is_highlighted = False
			self.color = Window.Button.COLOR
		
		def display(self, screen: Surface):
			pygame.draw.rect(screen, self.color, (*self.position, *self.size))
			self.text.display(screen)
		
		def highlight(self, mouse_x: int, mouse_y: int):
			if (
				self.hitbox[0] <= mouse_x < self.hitbox[2] and
				self.hitbox[1] <= mouse_y < self.hitbox[3]
				):
				self.is_highlighted = True
				self.color = Window.Button.HIGHLIGHT_COLOR
			else:
				self.is_highlighted = False
				self.color = Window.Button.COLOR
		
		def click(self):
			if self.is_highlighted:
				self.onclick()


	PANEL_WIDTH = 400
	PANEL_COLOR = (30, 30, 30)
	
	SIMULATION_WIDTH = 1200
	SIMULATION_HEIGHT = 900
	SIMULATION_COLUMNS = 8
	SIMULATION_ROWS = 6
	SIMULATION_NUM = SIMULATION_COLUMNS * SIMULATION_ROWS
	SIMULATION_SPEED = 0.1

	GAME_WIDTH = SIMULATION_WIDTH // SIMULATION_COLUMNS
	GAME_HEIGHT = SIMULATION_HEIGHT // SIMULATION_ROWS
	GAME_SPEED = SIMULATION_SPEED / SIMULATION_NUM

	PLAY_SPEED = 0.2
	VIEW_SPEED = 0.05

	WIDTH = SIMULATION_WIDTH + PANEL_WIDTH
	HEIGHT = SIMULATION_HEIGHT

	def set_mode_play(self):
		self.mode = Mode.PLAY
	
	def set_mode_simulate(self):
		self.mode = Mode.SIMULATE

	def set_mode_archive(self):
		self.mode = Mode.ARCHIVE

	def set_view_all(self):
		self.view = View.ALL

	def set_view_best(self):
		self.view = View.BEST

		if hasattr(self.game_view.controler, "network") and self.best_network != self.game_view.controler.network: # type: ignore
			self.game_view = Game(self.view_gamerules, NeuralControler(self.best_network, self.input_calculator))

	def __init__(self):

		# Enviorment setup
		pygame.init()
		pygame.display.set_caption("SnakeAI")
		self.screen = pygame.display.set_mode((Window.WIDTH, Window.HEIGHT))
		self.clock = pygame.time.Clock()
		self.is_running = True
		self.delta_time = 0
		
		# Display and control setup
		self.panel: Surface = pygame.Surface((Window.PANEL_WIDTH, Window.HEIGHT))
		title_font = pygame.font.Font("assets/Consolas.ttf", 40)
		info_font = pygame.font.Font("assets/Consolas.ttf", 20)

		self.title_text = Window.Text(title_font, "SnakeAI", (30, 20))
		self.credits_text = Window.Text(info_font, "by Tzu1", (Window.PANEL_WIDTH - 80, Window.HEIGHT - 25))

		self.mode: Mode = Mode.PLAY
		mode_play_button = Window.Button((30, 80), (75, 40), info_font, "Play", self.set_mode_play)
		mode_simulate_button = Window.Button((130, 80), (100, 40), info_font, "Simulate", self.set_mode_simulate)
		mode_archive_button = Window.Button((255, 80), (90, 40), info_font, "Archive", self.set_mode_archive)
		self.mode_buttons: List[Window.Button] = [mode_play_button, mode_simulate_button, mode_archive_button]

		play_text = Window.Text(info_font, "Press AWSD to move", (30, 140))
		self.play_texts: List[Window.Text] = [play_text]

		self.generation_text = Window.Text(info_font, "Generation: N/A", (30, 140))
		self.max_fitness_text = Window.Text(info_font, "Maximum fitness: N/A", (30, 170))
		self.avg_fitness_text = Window.Text(info_font, "Average fitness: N/A", (30, 200))
		self.simulate_texts: List[Window.Text] = [self.generation_text, self.max_fitness_text, self.avg_fitness_text]

		self.view: View = View.ALL
		self.view_all_button = Window.Button((30, 250), (110, 40), info_font, "View best", self.set_view_best)
		self.view_best_button = Window.Button((30, 250), (105, 40), info_font, "View all", self.set_view_all)

		# Simulation setup
		self.simulation_gamerules = Game.Rules(Window.GAME_WIDTH, Window.GAME_HEIGHT, 10, 10, 10)
		self.view_gamerules = Game.Rules(Window.SIMULATION_WIDTH, Window.SIMULATION_HEIGHT, 24, 18, -1)
		self.play_gamerules = Game.Rules(Window.SIMULATION_WIDTH, Window.SIMULATION_HEIGHT, 24, 18, -1, sys.maxsize)

		self.survival_size = Window.SIMULATION_NUM // 3
		self.generation_num = 0
		self.mutation_chance = 0.05
		self.parent_num = 2

		self.game_timer = 0
		self.game_delay = Window.GAME_SPEED
		self.current_game = 0
		self.games_over = 0

		self.network_constructor = NeuralControler.large_grid_network
		self.input_calculator = NeuralControler.large_grid_input

		self.networks: List[NeuralNetwork] = []
		self.games: List[Game] = []
		for _ in range(Window.SIMULATION_NUM):
			network = self.network_constructor()
			self.networks.append(network)
			self.games.append(Game(self.simulation_gamerules, NeuralControler(network, self.input_calculator)))
		self.game_play = Game(self.play_gamerules, ManualControler())
		self.game_view = Game(self.view_gamerules, self.games[0].controler)

		self.best_network = self.networks[0]
		self.best_score = 0

	def iterate_population(self):
		self.games_over = 0

		scores = []
		for game in self.games:
			scores.append(game.score)
		scores = np.array(scores)

		sorted_score_indices = np.argsort(scores)
		surviving_scores = np.array(scores)[sorted_score_indices][-self.survival_size:]
		surviving_networks = np.array(self.networks)[sorted_score_indices][-self.survival_size:]

		if surviving_scores[-1] > self.best_score:
			self.best_score = surviving_scores[-1]
			self.best_network = surviving_networks[-1]

		self.generation_text.change_text(f"Generation: {self.generation_num}")
		self.max_fitness_text.change_text(f"Maximum fitness: {int(np.max(surviving_scores))}")
		self.avg_fitness_text.change_text(f"Average fitness: {int(np.sum(surviving_scores) / surviving_scores.size)}")

		self.games = []
		self.networks = []
		for _ in range(Window.SIMULATION_NUM - self.survival_size):
			new_network = self.network_constructor()
			self.networks.append(new_network)

			parents: List[NeuralNetwork] = [surviving_networks[random.randint(0, self.survival_size-1)] for _ in range(self.parent_num)]
			GeneticAlgorithm.crossover(new_network, *parents)    
			GeneticAlgorithm.mutation(new_network, self.mutation_chance)

			new_game = Game(self.simulation_gamerules, NeuralControler(new_network, self.input_calculator))
			self.games.append(new_game)

		for surviving_network in surviving_networks:
			self.networks.append(surviving_network)
			surviving_game = Game(self.simulation_gamerules, NeuralControler(surviving_network, self.input_calculator))
			self.games.append(surviving_game)
		
		self.generation_num += 1
	
	def run_games(self):
		self.game_timer += self.delta_time
		if self.game_timer >= self.game_delay:
			game = self.games[self.current_game]

			if not game.is_over:
				self.game_timer -= self.game_delay
				game.play()

				if game.is_over:
					self.games_over += 1

				if self.games_over >= Window.SIMULATION_NUM:
					self.current_step = 0
					self.iterate_population()				

			self.current_game += 1
			if self.current_game >= Window.SIMULATION_NUM:
				self.current_game = 0
	
	def play_game(self):
		self.game_timer += self.delta_time
		if self.game_timer >= Window.PLAY_SPEED:
			self.game_play.play()

			if self.game_play.controler.action != Action.NONE:
				self.game_timer = 0

	def view_game(self):
		self.game_timer += self.delta_time
		if self.game_timer >= Window.VIEW_SPEED:
			self.game_view.play()
			self.game_timer = 0

		for _ in range(Window.SIMULATION_NUM * 20):
			game = self.games[self.current_game]
			if not game.is_over:
				game.play()

				if game.is_over:
					self.games_over += 1

				if self.games_over >= Window.SIMULATION_NUM:
					self.current_step = 0
					self.iterate_population()				

			self.current_game += 1
			if self.current_game >= Window.SIMULATION_NUM:
				self.current_game = 0
	
	def update(self):
		for event in pygame.event.get():			
			if event.type == pygame.QUIT:
				self.is_running = False

			elif event.type == pygame.MOUSEMOTION:
				mouse_x, mouse_y = event.pos
				for button in self.mode_buttons:
					button.highlight(mouse_x, mouse_y)
				
				if self.mode == Mode.SIMULATE:
					if self.view == View.ALL:
						self.view_all_button.highlight(mouse_x, mouse_y)
					else:
						self.view_best_button.highlight(mouse_x, mouse_y)

			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					for button in self.mode_buttons:
						button.click()
					
					if self.mode == Mode.SIMULATE:
						if self.view == View.ALL:
							self.view_all_button.click()
						else:
							self.view_best_button.click()
		
		if self.mode == Mode.PLAY:
			self.play_game()
		elif self.mode == Mode.SIMULATE:
			if self.view == View.BEST:
				self.view_game()
			else:
				self.run_games()
		else:
			self.view_game()
		

		self.delta_time = self.clock.tick() / 1000

	def render(self):
		# Simulation
		if self.mode == Mode.PLAY:
			self.game_play.display()
			self.screen.blit(self.game_play.surface, (0, 0))
		elif self.mode == Mode.SIMULATE:

			if self.view == View.ALL:
				for game_index in range(Window.SIMULATION_NUM):
					game = self.games[game_index]
					game.display()
					self.screen.blit(game.surface, (game_index // Window.SIMULATION_ROWS * Window.GAME_WIDTH, game_index % Window.SIMULATION_ROWS * Window.GAME_HEIGHT))
			else:
				self.game_view.display()
				self.screen.blit(self.game_view.surface, (0, 0))
		else:
			self.game_view.display()
			self.screen.blit(self.game_view.surface, (0, 0))

		# Panel
		self.panel.fill(Window.PANEL_COLOR)

		self.title_text.display(self.panel)
		self.credits_text.display(self.panel)

		for button in self.mode_buttons:
			button.display(self.panel)
		
		if self.mode == Mode.PLAY:
			for text in self.play_texts:
				text.display(self.panel)
		elif self.mode == Mode.SIMULATE:
			for text in self.simulate_texts:
				text.display(self.panel)
			
			if self.view == View.ALL:
				self.view_all_button.display(self.panel)
			else:
				self.view_best_button.display(self.panel)
		else:
			pass

		self.screen.blit(self.panel, (Window.SIMULATION_WIDTH, 0))

	  # Render
		pygame.display.flip()
	
	def run(self):
		while self.is_running:
			self.update()
			self.render()
		pygame.quit()
