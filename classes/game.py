import random
from classes.util import *
from classes.abstract import WindowComponent, Controler


class Game(WindowComponent):
    GRID_COLUMNS = 10
    GRID_ROWS = 10
    LINE_WIDTH = 1
    CELL_COUNT = GRID_COLUMNS * GRID_ROWS

    BACKGROUND_COLOR = (40, 40, 40)
    LINE_COLOR = (80, 80, 80)
    SNAKE_HEAD_COLOR = (0, 130, 0)
    SNAKE_BODY_COLOR = (0, 220, 0)
    APPLE_COLOR = (200, 0, 0)
    OVER_COLOR = (45, 35, 35)

    ACT_DELAY = 0.5

    @staticmethod
    def random_position() -> Vector2:
        return (random.randint(0, Game.GRID_COLUMNS-1), random.randint(0, Game.GRID_ROWS-1))

    def random_apple(self) -> Vector2:
        apple = Game.random_position()
        while apple in self.snake:
            apple = Game.random_position()
        return apple

    def __init__(self, width: int, height: int, controler: Controler):
        super().__init__(width, height)
        self.controler = controler
        
        self.cell_width = self.width // Game.GRID_COLUMNS
        self.cell_height = self.height // Game.GRID_ROWS
        self.grid: Array2D[Cell] = [[Cell.EMPTY for _ in range(Game.GRID_COLUMNS)] for _ in range(Game.GRID_ROWS)]
        
        self.snake: List[Vector2] = [Game.random_position()]
        self.grid[self.snake[0][1]][self.snake[0][0]] = Cell.FULL
        self.apple = self.random_apple()

        self.total_moves = 0
        self.feeding_moves = 0
        self.is_over = False
    
    def reset(self):
        self.grid: Array2D[Cell] = [[Cell.EMPTY for _ in range(Game.GRID_COLUMNS)] for _ in range(Game.GRID_ROWS)]
        
        self.snake: List[Vector2] = [Game.random_position()]
        self.grid[self.snake[0][1]][self.snake[0][0]] = Cell.FULL
        self.apple = self.random_apple()

    def move(self, direction: Vector2):
        new_x = self.snake[0][0] + direction[0]
        new_y = self.snake[0][1] + direction[1]

        if (
            not 0 <= new_x < Game.GRID_COLUMNS or 
            not 0 <= new_y < Game.GRID_ROWS or 
            self.grid[new_y][new_x] == Cell.FULL or 
            len(self.snake) + 2*Game.CELL_COUNT**0.5 < self.feeding_moves
            ):
            self.is_over = True
        else:
            snake_next = (new_x, new_y)
            self.grid[new_y][new_x] = Cell.FULL
            self.grid[self.snake[-1][1]][self.snake[-1][0]] = Cell.EMPTY
                
            for s in range(len(self.snake)):
                self.snake[s], snake_next = snake_next, self.snake[s]
            
            if self.apple == self.snake[0]:
                self.feeding_moves = 0

                self.grid[snake_next[1]][snake_next[0]] = Cell.FULL
                self.snake.append(snake_next)
                self.apple = self.random_apple()
        
        self.total_moves += 1
        self.feeding_moves += 1

    def update(self):

        action = self.controler.compute_action(self.grid, self.snake, self.apple)
        if action == Action.LEFT:
            self.move((-1, 0))
        elif action == Action.RIGHT:
            self.move((1, 0))
        elif action == Action.UP:
            self.move((0, -1))
        elif action == Action.DOWN:
            self.move((0, 1))
        
        return self.is_over

    def cell_to_screen(self, cell_position: Vector2) -> Vector2:
        return (cell_position[0] * self.cell_width, cell_position[1] * self.cell_height)
    
    def display_cell(self, position: Vector2, color: Vector3):
        screen_position = self.cell_to_screen(position)
        pygame.draw.rect(self.surface, color, (screen_position[0] + Game.LINE_WIDTH, screen_position[1] + Game.LINE_WIDTH, self.cell_width - Game.LINE_WIDTH, self.cell_height - Game.LINE_WIDTH))

    def display(self):
        # Background
        if not self.is_over:
            super().display()
        else:
            self.surface.fill(self.OVER_COLOR)

        # Grid lines
        for row in range(Game.GRID_ROWS):
            """for col in range(Game.GRID_COLUMNS):
                row_end =  (row + 1) * self.cell_height
                col_end = (col + 1) * self.cell_width
                pygame.draw.line(self.surface, Game.LINE_COLOR, (0, row_end), (col_end, row_end), Game.LINE_WIDTH)
                pygame.draw.line(self.surface, Game.LINE_COLOR, (col_end, 0), (col_end, row_end), Game.LINE_WIDTH)"""
            pygame.draw.rect(self.surface, Game.LINE_COLOR, (0, 0, self.width-1, self.height-Game.LINE_WIDTH), Game.LINE_WIDTH)

        # Snake
        for snake_cell in self.snake:
            self.display_cell(snake_cell, Game.SNAKE_BODY_COLOR)
        self.display_cell(self.snake[0], Game.SNAKE_HEAD_COLOR)
        
        # Apple
        self.display_cell(self.apple, Game.APPLE_COLOR)
