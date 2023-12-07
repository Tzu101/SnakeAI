import random
from classes.util import *
from classes.abstract import Controler


class Game:

    class Rules:

        def __init__(self, width: int, height: int, columns: int, rows: int, lives: int, move_limit=None):
            self.width = width
            self.height = height
            self.columns = columns
            self.rows = rows
            self.lives = lives

            self.cell_width = width // columns
            self.cell_height = height // rows
            self.cells = columns * rows
            self.move_limit = (columns * rows) / 2 if not move_limit else move_limit

    BACKGROUND_COLOR = (10, 10, 30)
    LINE_COLOR = (80, 80, 80)
    SNAKE_HEAD_COLOR = (0, 130, 0)
    SNAKE_BODY_COLOR = (0, 220, 0)
    APPLE_COLOR = (200, 0, 0)

    def random_position(self) -> Vector2:
        return (random.randint(0, self.rules.columns-1), random.randint(0, self.rules.rows-1))

    def random_apple(self) -> Vector2:
        apple = self.random_position()
        while apple in self.snake:
            apple = self.random_position()
        return apple

    def grid_add_snake(self, snake_body: Vector2):
        self.grid[snake_body[1]][snake_body[0]] = Cell.FULL
    
    def random_snake(self) -> List[Vector2]:
        snake = self.random_position()
        self.grid_add_snake(snake)
        return [snake]
    
    def find_snake_part(self, pos: Vector2):
        for s in range(len(self.snake)):
            if self.snake[s][0] == pos[0] and self.snake[s][1] == pos[1]:
                return s
        return -1

    def __init__(self, rules, controler: Controler):
        self.rules: Game.Rules = rules
        self.controler = controler

        self.surface: Surface = pygame.Surface((self.rules.width, self.rules.height))
        
        self.grid: Array2D[Cell] = []
        self.heatmap: Array2D[int] = []
        for row in range(self.rules.rows):
            self.grid.append([])
            self.heatmap.append([])
            for _ in range(self.rules.columns):
                self.grid[row].append(Cell.EMPTY)
                self.heatmap[row].append(0)

        self.snake: List[Vector2] = self.random_snake()
        self.apple = self.random_apple()
        
        self.moves = 0
        self.lives = self.rules.lives

        self.score = 0
        self.is_over = False
    
    def reset(self):
        self.moves = 0

        self.grid: Array2D[Cell] = []
        self.heatmap: Array2D[int] = []
        for row in range(self.rules.rows):
            self.grid.append([])
            self.heatmap.append([])
            for _ in range(self.rules.columns):
                self.grid[row].append(Cell.EMPTY)
                self.heatmap[row].append(0)

        self.snake: List[Vector2] = self.random_snake()
        self.apple = self.random_apple()
    
    def death(self):
        self.lives -= 1
        if self.lives != 0:
            self.reset()
        else:
            self.is_over = True

    def move(self, direction: Vector2):
        new_x = self.snake[0][0] + direction[0]
        new_y = self.snake[0][1] + direction[1]

        if not 0 <= new_x < self.rules.columns:
            self.score -= 2
            self.death()
        elif not 0 <= new_y < self.rules.rows:
            self.score -= 2
            self.death()
        elif self.grid[new_y][new_x] == Cell.FULL:
            hit_index = self.find_snake_part((new_x, new_y))
            if hit_index == -1:
                pass
                self.score -= 1
            else:
                pass
                # (1, 2]
                self.score -= (len(self.snake) - hit_index) / (len(self.snake) - 1) + 1
            self.death()
        elif len(self.snake) + self.rules.move_limit < self.moves:
            heatmap = np.array(self.heatmap).flatten()
            non_zero = np.where(heatmap != 0)[0]

            non_zero_heatmap = heatmap[non_zero]
            non_zero_penalty = (self.rules.cells - non_zero.size) / self.rules.cells

            max_indices = np.argsort(non_zero_heatmap)[-max(int(non_zero.size * 0.1), len(self.snake)+1):]
            clump_penalty = np.sum(non_zero_heatmap[max_indices]) / np.sum(non_zero_heatmap)

            # (0, 2)
            final_penalty = non_zero_penalty + clump_penalty
            self.score -= final_penalty
            self.death()
        else:
            self.moves += 1
            self.heatmap[new_y][new_x] += 1

            snake_next = (new_x, new_y)
            self.grid[new_y][new_x] = Cell.FULL
            self.grid[self.snake[-1][1]][self.snake[-1][0]] = Cell.EMPTY
                
            for s in range(len(self.snake)):
                self.snake[s], snake_next = snake_next, self.snake[s]
            
            if self.apple == self.snake[0]:
                self.score += 1
                self.moves = 0

                self.grid[snake_next[1]][snake_next[0]] = Cell.FULL
                self.snake.append(snake_next)
                self.apple = self.random_apple()

    def play(self):

        if self.is_over:
            return
        

        action = self.controler.compute_action(self.grid, self.snake, self.apple)
        if action == Action.LEFT:
            self.move((-1, 0))
        elif action == Action.RIGHT:
            self.move((1, 0))
        elif action == Action.UP:
            self.move((0, -1))
        elif action == Action.DOWN:
            self.move((0, 1))
    
    def display_cell(self, position: Vector2, color: Vector3):
        pygame.draw.rect(self.surface, color, (
            (position[0] * self.rules.cell_width) + 1, 
            (position[1] * self.rules.cell_height) + 1, 
            self.rules.cell_width-2, 
            self.rules.cell_height-2
            ))

    def display(self):
        # Background
        pygame.draw.rect(self.surface, Game.BACKGROUND_COLOR, (0, 0, self.rules.width, self.rules.height))
        if self.is_over:
            self.surface.set_alpha(127)
        else:
            self.surface.set_alpha(255)

        # Grid lines
        pygame.draw.rect(self.surface, Game.LINE_COLOR, (0, 0, self.rules.width, self.rules.height), 1)

        # Snake
        for snake_cell in self.snake:
            self.display_cell(snake_cell, Game.SNAKE_BODY_COLOR)
        self.display_cell(self.snake[0], Game.SNAKE_HEAD_COLOR)
        
        # Apple
        self.display_cell(self.apple, Game.APPLE_COLOR)
