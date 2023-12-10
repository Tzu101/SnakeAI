import sys
from classes.util import *
from classes.game import Game
from classes.network import NeuralNetwork, GeneticAlgorithm
from classes.controler import ManualControler, NeuralControler, DummyControler


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
		BODY_COLOR = (70, 70, 70)
		BORDER_COLOR = (50, 50, 50)
		HIGHLIGHT_COLOR = (90, 90, 90)

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
			self.body_color = Window.Button.BODY_COLOR
			self.border_color = Window.Button.BORDER_COLOR
		
		def display(self, screen: Surface):
			pygame.draw.rect(screen, self.body_color, (*self.position, *self.size))
			pygame.draw.rect(screen, self.border_color, (*self.position, *self.size), 4)
			self.text.display(screen)
		
		def highlight(self, mouse_x: int, mouse_y: int):
			if (
				self.hitbox[0] <= mouse_x < self.hitbox[2] and
				self.hitbox[1] <= mouse_y < self.hitbox[3]
				):
				self.is_highlighted = True
				self.border_color = Window.Button.HIGHLIGHT_COLOR
			else:
				self.is_highlighted = False
				self.border_color = Window.Button.BORDER_COLOR
		
		def click(self):
			if self.is_highlighted:
				self.onclick()

	
	class Switch(Button):
		SUPER_HIGHLIGHT_COLOR = (110, 110, 110)

		def __init__(self, position: Vector2, size: Vector2, font, text, onclick: Callable):
			super().__init__(position, size, font, text, onclick)
			self.is_toggled = False
		
		def highlight(self, mouse_x: int, mouse_y: int):
			if (
				self.hitbox[0] <= mouse_x < self.hitbox[2] and
				self.hitbox[1] <= mouse_y < self.hitbox[3]
				):
				self.is_highlighted = True
				if self.is_toggled:
					self.border_color = Window.Switch.SUPER_HIGHLIGHT_COLOR
				else:
					self.border_color = Window.Button.HIGHLIGHT_COLOR
			else:
				self.is_highlighted = False
				if self.is_toggled:
					self.border_color = Window.Switch.BODY_COLOR
				else:
					self.border_color = Window.Button.BORDER_COLOR
		
		def click(self):
			if self.is_highlighted:
				self.is_toggled = not self.is_toggled
				if self.is_toggled:
					self.body_color = Window.Button.HIGHLIGHT_COLOR
				else:
					self.body_color = Window.Button.BODY_COLOR
				self.onclick(self.is_toggled)

		def set_clicked(self, is_clicked: bool):
			self.is_toggled = is_clicked
			if self.is_toggled:
				self.body_color = Window.Button.HIGHLIGHT_COLOR
			else:
				self.body_color = Window.Button.BODY_COLOR


	PANEL_WIDTH = 400
	PANEL_COLOR = (30, 30, 30)
	
	SIMULATION_WIDTH = 1200
	SIMULATION_HEIGHT = 900
	SIMULATION_COLUMNS = 12
	SIMULATION_ROWS = 9
	SIMULATION_NUM = SIMULATION_COLUMNS * SIMULATION_ROWS
	SIMULATION_SPEED = 0.1

	GAME_WIDTH = SIMULATION_WIDTH // SIMULATION_COLUMNS
	GAME_HEIGHT = SIMULATION_HEIGHT // SIMULATION_ROWS

	PLAY_SPEED = 0.1
	VIEW_SPEED = 0.05

	WIDTH = SIMULATION_WIDTH + PANEL_WIDTH
	HEIGHT = SIMULATION_HEIGHT

	def screenshot(self):
		#rect = pygame.Rect(0, 0, Window.WIDTH, Window.HEIGHT)
		#sub = self.screen.subsurface(rect)
		pygame.image.save(self.screen, "screenshot.png")

	def select_update_and_display(self, mode: Mode, view: View=View.ALL):
		if mode == Mode.PLAY:
			self.update_selected = self.update_play
			self.display_selected = self.display_play
		elif mode == Mode.SIMULATE:
			if view == View.ALL:
				self.update_selected = self.update_simulate_all
				self.display_selected = self.display_simulate_all
			else:
				self.update_selected = self.update_simulate_best
				self.display_selected = self.display_simulate_best
		elif mode == Mode.ARCHIVE:
			self.update_selected = self.update_archive
			self.display_selected = self.display_archive

	def select_play(self, *args):
		self.play_button.set_clicked(True)
		self.simulate_button.set_clicked(False)
		self.archive_button.set_clicked(False)
		self.select_update_and_display(Mode.PLAY)

	def select_simulate_all(self, *args):
		self.play_button.set_clicked(False)
		self.simulate_button.set_clicked(True)
		self.archive_button.set_clicked(False)
		self.select_update_and_display(Mode.SIMULATE, View.ALL)

	def select_simulate_best(self):
		self.select_update_and_display(Mode.SIMULATE, View.BEST)

		if not hasattr(self.best_game.controler, "network") or self.best_network != self.best_game.controler.network: # type: ignore
			self.best_game = Game(self.view_gamerules, NeuralControler(self.best_network, self.input_calculator))

	def select_archive(self, *args):
		self.play_button.set_clicked(False)
		self.simulate_button.set_clicked(False)
		self.archive_button.set_clicked(True)
		self.select_update_and_display(Mode.ARCHIVE)
		self.binary_archive_button.onclick()

	def accelerate_simulation(self, do_acc: bool):
		if do_acc:
			self.simulation_speed = 0
			self.simulation_iterations = lambda : int(1 / self.delta_time) + 1
		else:
			self.simulation_speed = Window.SIMULATION_SPEED
			self.simulation_iterations = lambda : 1
	
	def load_archive(self, file_name: str, input_calculator: Callable, type: NetworkType):

		def load_archive_wrapped(*args):
			self.binary_archive_button.set_clicked(False)
			self.numeric_archive_button.set_clicked(False)
			self.small_grid_archive_button.set_clicked(False)
			self.large_grid_archive_button.set_clicked(False)

			if type == NetworkType.BINARY:
				self.binary_archive_button.set_clicked(True)
			elif type == NetworkType.NUMERIC:
				self.numeric_archive_button.set_clicked(True)
			elif type == NetworkType.SMALL_GRID:
				self.small_grid_archive_button.set_clicked(True)
			elif type == NetworkType.LARGE_GRID:
				self.large_grid_archive_button.set_clicked(True)

			network = NeuralNetwork.load(file_name)
			self.archive_game = Game(self.view_gamerules, NeuralControler(network, input_calculator))

		return load_archive_wrapped
	
	def change_simulation(self, network_constructor: Callable, input_calculator: Callable, type: NetworkType):

		def change_simulation_wrapped(*args):
			self.binary_simulation_button.set_clicked(False)
			self.numeric_simulation_button.set_clicked(False)
			self.small_grid_simulation_button.set_clicked(False)
			self.large_grid_simulation_button.set_clicked(False)

			if type == NetworkType.BINARY:
				self.binary_simulation_button.set_clicked(True)
			elif type == NetworkType.NUMERIC:
				self.numeric_simulation_button.set_clicked(True)
			elif type == NetworkType.SMALL_GRID:
				self.small_grid_simulation_button.set_clicked(True)
			elif type == NetworkType.LARGE_GRID:
				self.large_grid_simulation_button.set_clicked(True)

			self.network_constructor = network_constructor
			self.input_calculator = input_calculator
			self.simulation_reset()

		return change_simulation_wrapped

	def __init__(self):

		# Enviorment setup
		pygame.init()
		pygame.display.set_caption("SnakeAI")
		self.screen = pygame.display.set_mode((Window.WIDTH, Window.HEIGHT))
		self.clock = pygame.time.Clock()
		self.is_running = True
		self.delta_time = 0
		
		# Display and control setu
		self.update_selected = self.update_play
		self.display_selected = self.display_play

		self.panel: Surface = pygame.Surface((Window.PANEL_WIDTH, Window.HEIGHT))
		title_font = pygame.font.Font("assets/Consolas.ttf", 40)
		info_font = pygame.font.Font("assets/Consolas.ttf", 20)

		self.title_text = Window.Text(title_font, "SnakeAI", (30, 20))
		self.credits_text = Window.Text(info_font, "by Tzu1", (Window.PANEL_WIDTH - 80, Window.HEIGHT - 25))

		self.play_button = Window.Switch((30, 80), (75, 40), info_font, "Play", self.select_play)
		self.simulate_button = Window.Switch((115, 80), (100, 40), info_font, "Simulate", self.select_simulate_all)
		self.archive_button = Window.Switch((225, 80), (90, 40), info_font, "Archive", self.select_archive)
		self.play_button.set_clicked(True)

		self.play_text = Window.Text(info_font, "Press AWSD to move", (30, 140))
		self.score_text = Window.Text(info_font, "Score: 0", (30, 170))

		self.generation_text = Window.Text(info_font, "Generation: 0", (30, 140))
		self.max_fitness_text = Window.Text(info_font, "Maximum fitness: N/A", (30, 170))
		self.avg_fitness_text = Window.Text(info_font, "Average fitness: N/A", (30, 200))

		self.accelerate_simulation_switch = Window.Switch((30, 240), (110, 40), info_font, "Speed up", self.accelerate_simulation)
		self.simulation_reset_button = Window.Switch((150, 240), (110, 40), info_font, "Reset", self.simulation_reset)
		self.simulate_best_button = Window.Button((270, 240), (110, 40), info_font, "View best", self.select_simulate_best)
		self.simulate_all_button = Window.Button((270, 240), (105, 40), info_font, "View all", self.select_simulate_all)

		self.binary_simulation_text = Window.Text(info_font, "(12)->tanh(8)->(4)", (150, 315))
		self.numeric_simulation_text = Window.Text(info_font, "(24)->tanh(10)->(4)", (150, 365))
		self.small_grid_simulation_text = Window.Text(info_font, "(13)->tanh(8)->(4)", (150, 415))
		self.large_grid_simulation_text = Window.Text(info_font, "(53)->tanh(16)->(4)", (150, 465))

		self.binary_simulation_button = Window.Switch((30, 305), (105, 40), info_font, "Binary", self.change_simulation(NeuralControler.binary_network, NeuralControler.binary_input, NetworkType.BINARY))
		self.numeric_simulation_button = Window.Switch((30, 355), (105, 40), info_font, "Numberic", self.change_simulation(NeuralControler.numeric_network, NeuralControler.numeric_input, NetworkType.NUMERIC))
		self.small_grid_simulation_button = Window.Switch((30, 405), (105, 40), info_font, "Grid 3x3", self.change_simulation(NeuralControler.small_grid_network, NeuralControler.small_grid_input, NetworkType.SMALL_GRID))
		self.large_grid_simulation_button = Window.Switch((30, 455), (105, 40), info_font, "Grid 7x7", self.change_simulation(NeuralControler.large_grid_network, NeuralControler.large_grid_input, NetworkType.LARGE_GRID))

		self.archive_text = Window.Text(info_font, "Select a network to run", (30, 140))

		self.binary_archive_text = Window.Text(info_font, "Fitness: 240", (150, 190))
		self.numeric_archive_text = Window.Text(info_font, "Fitness: 195", (150, 240))
		self.small_grid_archive_text = Window.Text(info_font, "Fitness: 240", (150, 290))
		self.large_grid_archive_text = Window.Text(info_font, "Fitness: 231", (150, 340))

		self.binary_archive_button = Window.Switch((30, 180), (105, 40), info_font, "Binary", self.load_archive("binary_240", NeuralControler.binary_input, NetworkType.BINARY))
		self.numeric_archive_button = Window.Switch((30, 230), (105, 40), info_font, "Numberic", self.load_archive("numeric_195", NeuralControler.numeric_input, NetworkType.NUMERIC))
		self.small_grid_archive_button = Window.Switch((30, 280), (105, 40), info_font, "Grid 3x3", self.load_archive("small_grid_240", NeuralControler.small_grid_input, NetworkType.SMALL_GRID))
		self.large_grid_archive_button = Window.Switch((30, 330), (105, 40), info_font, "Grid 7x7", self.load_archive("large_grid_231", NeuralControler.large_grid_input, NetworkType.LARGE_GRID))

		# Simulation setup
		self.simulation_gamerules = Game.Rules(Window.GAME_WIDTH, Window.GAME_HEIGHT, 10, 10, 10)
		self.view_gamerules = Game.Rules(Window.SIMULATION_WIDTH, Window.SIMULATION_HEIGHT, 24, 18, -1)
		self.play_gamerules = Game.Rules(Window.SIMULATION_WIDTH, Window.SIMULATION_HEIGHT, 24, 18, -1, sys.maxsize)

		self.survival_size = Window.SIMULATION_NUM // 4
		self.generation_num = 0
		self.mutation_chance = 0.1
		self.parent_num = 2

		self.play_timer = 0
		self.simulate_best_timer = 0
		self.archive_timer = 0

		self.simulate_all_timer = 0
		self.simulation_speed = Window.SIMULATION_SPEED
		self.simulation_iterations = lambda : 1
		self.games_over = 0

		self.networks: List[NeuralNetwork] = []
		self.simulated_games: List[Game] = []

		self.play_game = Game(self.play_gamerules, ManualControler())
		self.best_game = Game(self.view_gamerules, DummyControler())
		self.archive_game = Game(self.view_gamerules, DummyControler())

		self.best_network = NeuralNetwork(0)
		self.best_score = -sys.maxsize

		self.network_constructor = NeuralControler.binary_network
		self.input_calculator = NeuralControler.binary_input
		self.binary_simulation_button.onclick()

	def simulation_reset(self):
		self.games_over = 0
		self.simulate_all_timer = 0
		self.generation_num = 0

		self.generation_text.change_text("Generation: 0")
		self.max_fitness_text.change_text("Maximum fitness: N/A")
		self.avg_fitness_text.change_text("Average fitness: N/A")

		self.networks: List[NeuralNetwork] = []
		self.simulated_games: List[Game] = []
		for _ in range(Window.SIMULATION_NUM):
			network = self.network_constructor()
			self.networks.append(network)
			self.simulated_games.append(Game(self.simulation_gamerules, NeuralControler(network, self.input_calculator)))
		self.best_score = -sys.maxsize
		self.best_network = self.networks[0]

	def simulate_next_generation(self):
		self.games_over = 0
		self.generation_num += 1

		scores = []
		for game in self.simulated_games:
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

		self.simulated_games = []
		self.networks = []
		for _ in range(Window.SIMULATION_NUM - self.survival_size):
			new_network = self.network_constructor()
			self.networks.append(new_network)

			parents: List[NeuralNetwork] = [surviving_networks[random.randint(0, self.survival_size-1)] for _ in range(self.parent_num)]
			GeneticAlgorithm.crossover(new_network, *parents)    
			GeneticAlgorithm.mutation(new_network, self.mutation_chance)

			new_game = Game(self.simulation_gamerules, NeuralControler(new_network, self.input_calculator))
			self.simulated_games.append(new_game)

		for surviving_network in surviving_networks:
			self.networks.append(surviving_network)
			surviving_game = Game(self.simulation_gamerules, NeuralControler(surviving_network, self.input_calculator))
			self.simulated_games.append(surviving_game)
	
	def update_simulated_games(self):
		self.simulate_all_timer += self.delta_time
		if self.simulate_all_timer >= self.simulation_speed:
			self.simulate_all_timer = 0

			for _ in range(self.simulation_iterations()):
				for g in range(Window.SIMULATION_NUM):
					game = self.simulated_games[g]

					if not game.is_over:
						game.update()

						if game.is_over:
							self.games_over += 1

						if self.games_over >= Window.SIMULATION_NUM:
							self.current_step = 0
							self.simulate_next_generation()				
	
	def update_play(self, events: List[Event]):
		self.play_timer += self.delta_time
		if self.play_timer >= Window.PLAY_SPEED:
			self.play_game.update()

			if self.play_game.controler.action != Action.NONE:
				self.play_timer = 0
		
		self.score_text.change_text(f"Score: {self.play_game.score}")

	def update_simulate_all(self, events: List[Event]):
		for event in events:			
			if event.type == pygame.MOUSEMOTION:
				mouse_x, mouse_y = event.pos
				self.accelerate_simulation_switch.highlight(mouse_x, mouse_y)
				self.simulation_reset_button.highlight(mouse_x, mouse_y)
				self.simulate_best_button.highlight(mouse_x, mouse_y)

				self.binary_simulation_button.highlight(mouse_x, mouse_y)
				self.numeric_simulation_button.highlight(mouse_x, mouse_y)
				self.small_grid_simulation_button.highlight(mouse_x, mouse_y)
				self.large_grid_simulation_button.highlight(mouse_x, mouse_y)

			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					self.accelerate_simulation_switch.click()
					self.simulation_reset_button.click()
					self.simulate_best_button.click()

					self.binary_simulation_button.click()
					self.numeric_simulation_button.click()
					self.small_grid_simulation_button.click()
					self.large_grid_simulation_button.click()

		self.update_simulated_games()

	def update_simulate_best(self, events: List[Event]):
		for event in events:			
			if event.type == pygame.MOUSEMOTION:
				mouse_x, mouse_y = event.pos
				self.accelerate_simulation_switch.highlight(mouse_x, mouse_y)
				self.simulation_reset_button.highlight(mouse_x, mouse_y)
				self.simulate_all_button.highlight(mouse_x, mouse_y)

			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					self.accelerate_simulation_switch.click()
					self.simulation_reset_button.click()
					self.simulate_all_button.click()
		
		self.update_simulated_games()
		self.simulate_best_timer += self.delta_time
		if self.simulate_best_timer >= Window.VIEW_SPEED:
			self.simulate_best_timer = 0
			self.best_game.update()

	def update_archive(self, events: List[Event]):
		for event in events:			
			if event.type == pygame.MOUSEMOTION:
				mouse_x, mouse_y = event.pos
				self.binary_archive_button.highlight(mouse_x, mouse_y)
				self.numeric_archive_button.highlight(mouse_x, mouse_y)
				self.small_grid_archive_button.highlight(mouse_x, mouse_y)
				self.large_grid_archive_button.highlight(mouse_x, mouse_y)

			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					self.binary_archive_button.click()
					self.numeric_archive_button.click()
					self.small_grid_archive_button.click()
					self.large_grid_archive_button.click()

		self.archive_timer += self.delta_time
		if self.archive_timer >= Window.VIEW_SPEED:
			self.archive_timer = 0
			self.archive_game.update()
	
	def update(self):
		events = pygame.event.get()
		for event in events:			
			if event.type == pygame.QUIT:
				self.is_running = False

			elif event.type == pygame.KEYDOWN and event.key == pygame.K_F2:
				self.screenshot()

			elif event.type == pygame.MOUSEMOTION:
				mouse_x, mouse_y = event.pos
				self.play_button.highlight(mouse_x, mouse_y)
				self.simulate_button.highlight(mouse_x, mouse_y)
				self.archive_button.highlight(mouse_x, mouse_y)

			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					self.play_button.click()
					self.simulate_button.click()
					self.archive_button.click()
		
		self.update_selected(events)
	
	def display_play(self):
		self.play_game.display()
		self.screen.blit(self.play_game.surface, (0, 0))
		
		self.play_text.display(self.panel)
		self.score_text.display(self.panel)

	def display_simulate(self):
		self.generation_text.display(self.panel)
		self.max_fitness_text.display(self.panel)
		self.avg_fitness_text.display(self.panel)
		self.accelerate_simulation_switch.display(self.panel)
		self.simulation_reset_button.display(self.panel)

	def display_simulate_all(self):
		self.display_simulate()
		self.simulate_best_button.display(self.panel)

		self.binary_simulation_text.display(self.panel)
		self.numeric_simulation_text.display(self.panel)
		self.small_grid_simulation_text.display(self.panel)
		self.large_grid_simulation_text.display(self.panel)

		self.binary_simulation_button.display(self.panel)
		self.numeric_simulation_button.display(self.panel)
		self.small_grid_simulation_button.display(self.panel)
		self.large_grid_simulation_button.display(self.panel)

		for game_index in range(Window.SIMULATION_NUM):
			game = self.simulated_games[game_index]
			game.display()
			self.screen.blit(
				game.surface, 
				(game_index // Window.SIMULATION_ROWS * Window.GAME_WIDTH, game_index % Window.SIMULATION_ROWS * Window.GAME_HEIGHT)
			)

	def display_simulate_best(self):
		self.display_simulate()
		self.simulate_all_button.display(self.panel)

		self.best_game.display()
		self.screen.blit(self.best_game.surface, (0, 0))

	def display_archive(self):
		self.archive_text.display(self.panel)
		self.binary_archive_text.display(self.panel)
		self.numeric_archive_text.display(self.panel)
		self.small_grid_archive_text.display(self.panel)
		self.large_grid_archive_text.display(self.panel)

		self.binary_archive_button.display(self.panel)
		self.numeric_archive_button.display(self.panel)
		self.small_grid_archive_button.display(self.panel)
		self.large_grid_archive_button.display(self.panel)

		self.archive_game.display()
		self.screen.blit(self.archive_game.surface, (0, 0))

	def display(self):
		pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, Window.SIMULATION_WIDTH, Window.SIMULATION_HEIGHT))
		self.panel.fill(Window.PANEL_COLOR)

		self.title_text.display(self.panel)
		self.credits_text.display(self.panel)
		self.play_button.display(self.panel)
		self.simulate_button.display(self.panel)
		self.archive_button.display(self.panel)

		self.display_selected()
		self.screen.blit(self.panel, (Window.SIMULATION_WIDTH, 0))

	  # Render
		pygame.display.flip()
	
	def run(self):
		while self.is_running:
			self.update()
			self.display()
			self.delta_time = self.clock.tick() / 1000
		pygame.quit()
