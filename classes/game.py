import random
from classes.util import *
from classes.abstract import WindowComponent
from classes.controler import ManualControler


class Game(WindowComponent):
    GRID_COLUMNS = 10
    GRID_ROWS = 10
    LINE_WIDTH = 2

    BACKGROUND_COLOR = (40, 40, 40)
    LINE_COLOR = (80, 80, 80)
    SNAKE_HEAD_COLOR = (20, 150, 20)
    SNAKE_BODY_COLOR = (50, 200, 50)
    APPLE_COLOR = (200, 50, 50)

    ACT_DELAY = 0.1

    @staticmethod
    def random_position() -> Vector2:
        return (random.randint(0, Game.GRID_COLUMNS-1), random.randint(0, Game.GRID_ROWS-1))

    def random_apple(self) -> Vector2:
        apple = Game.random_position()
        while apple in self.snake:
            apple = Game.random_position()
        return apple

    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        
        self.cell_width = self.width // Game.GRID_COLUMNS
        self.cell_height = self.height // Game.GRID_ROWS
        self.grid: Array2D[Cell] = [[Cell.EMPTY for _ in range(Game.GRID_COLUMNS)] for _ in range(Game.GRID_ROWS)]
        
        self.snake: List[Vector2] = [Game.random_position()]
        self.grid[self.snake[0][1]][self.snake[0][0]] = Cell.FULL
        self.apple = self.random_apple()

        self.act_timer = 0
        self.controler = ManualControler()
    
    def reset(self):
        self.grid: Array2D[Cell] = [[Cell.EMPTY for _ in range(Game.GRID_COLUMNS)] for _ in range(Game.GRID_ROWS)]
        
        self.snake: List[Vector2] = [Game.random_position()]
        self.grid[self.snake[0][1]][self.snake[0][0]] = Cell.FULL
        self.apple = self.random_apple()

        self.act_timer = 0
        self.controler = ManualControler()

    def move(self, direction: Vector2):
        new_x = self.snake[0][0] + direction[0]
        new_y = self.snake[0][1] + direction[1]

        if new_x < 0:
            new_x += Game.GRID_COLUMNS
        if new_x >= Game.GRID_COLUMNS:
            new_x -= Game.GRID_COLUMNS

        if new_y < 0:
            new_y += Game.GRID_ROWS
        if new_y >= Game.GRID_ROWS:
            new_y -= Game.GRID_ROWS

        if self.grid[new_y][new_x] == Cell.FULL:
            self.reset()
        else:
            snake_next = (new_x, new_y)
            self.grid[new_y][new_x] = Cell.FULL
            self.grid[self.snake[-1][1]][self.snake[-1][0]] = Cell.EMPTY
                
            for s in range(len(self.snake)):
                self.snake[s], snake_next = snake_next, self.snake[s]
            
            if self.apple == self.snake[0]:
                self.grid[snake_next[1]][snake_next[0]] = Cell.FULL
                self.snake.append(snake_next)
                self.apple = self.random_apple()

    def act(self, action: Action):
        if action == Action.LEFT:
            self.move((-1, 0))
        elif action == Action.RIGHT:
            self.move((1, 0))
        elif action == Action.UP:
            self.move((0, -1))
        elif action == Action.DOWN:
            self.move((0, 1))

    def update(self, dt: float):

        self.act_timer += dt
        if self.act_timer >= Game.ACT_DELAY:
            action = self.controler.compute_action(self.grid, self.snake, self.apple)

            if (action != Action.NONE):
                self.act_timer = 0
                self.act(action)

    
    def cell_to_screen(self, cell_position: Vector2) -> Vector2:
        return (cell_position[0] * self.cell_width, cell_position[1] * self.cell_height)
    
    def display_cell(self, position: Vector2, color: Vector3):
        screen_position = self.cell_to_screen(position)
        pygame.draw.rect(self.surface, color, (screen_position[0] + Game.LINE_WIDTH, screen_position[1] + Game.LINE_WIDTH, self.cell_width - Game.LINE_WIDTH, self.cell_height - Game.LINE_WIDTH))

    def display(self):
        # Background
        super().display()

        # Grid lines
        for row in range(Game.GRID_ROWS):
            for col in range(Game.GRID_COLUMNS):
                row_end =  (row + 1) * self.cell_height
                col_end = (col + 1) * self.cell_width
                pygame.draw.line(self.surface, Game.LINE_COLOR, (0, row_end), (col_end, row_end), Game.LINE_WIDTH)
                pygame.draw.line(self.surface, Game.LINE_COLOR, (col_end, 0), (col_end, row_end), Game.LINE_WIDTH)
            pygame.draw.rect(self.surface, Game.LINE_COLOR, (0, 0, self.width-1, self.height-Game.LINE_WIDTH), Game.LINE_WIDTH)

        # Snake
        for snake_cell in self.snake:
            self.display_cell(snake_cell, Game.SNAKE_BODY_COLOR)
        self.display_cell(self.snake[0], Game.SNAKE_HEAD_COLOR)
        
        # Apple
        self.display_cell(self.apple, Game.APPLE_COLOR)
