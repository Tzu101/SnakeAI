import random
from classes.util import *
from classes.abstract import WindowComponent, Controler


class Game(WindowComponent):
    GRID_COLUMNS = 20
    GRID_ROWS = 20
    GRID_DIAGONAL = int((GRID_COLUMNS**2 + GRID_ROWS**2)**0.5)
    GRID_SIZE = GRID_COLUMNS * GRID_ROWS

    BACKGROUND_COLOR = (40, 40, 40)
    LINE_COLOR = (80, 80, 80)
    SNAKE_HEAD_COLOR = (0, 130, 0)
    SNAKE_BODY_COLOR = (0, 220, 0)
    APPLE_COLOR = (200, 0, 0)
    OVER_COLOR = (45, 35, 35)

    @staticmethod
    def random_position() -> Vector2:
        return (random.randint(0, Game.GRID_COLUMNS-1), random.randint(0, Game.GRID_ROWS-1))

    def random_apple(self) -> Vector2:
        apple = Game.random_position()
        while apple in self.snake:
            apple = Game.random_position()
        return apple

    def grid_add_snake(self, snake_body: Vector2):
        self.grid[snake_body[1]][snake_body[0]] = Cell.FULL
    
    def random_snake(self) -> List[Vector2]:
        snake = Game.random_position()
        self.grid_add_snake(snake)
        return [snake]
    
    def find_snake_part(self, pos: Vector2):
        for s in range(len(self.snake)):
            if self.snake[s][0] == pos[0] and self.snake[s][1] == pos[1]:
                return s
        return -1

    def __init__(self, width: int, height: int, controler: Controler):
        super().__init__(width, height)
        self.controler = controler
        
        self.cell_width = self.width // Game.GRID_COLUMNS
        self.cell_height = self.height // Game.GRID_ROWS
        self.grid: Array2D[Cell] = [[Cell.EMPTY for _ in range(Game.GRID_COLUMNS)] for _ in range(Game.GRID_ROWS)]
        self.heatmap: Array2D[int] = [[0 for _ in range(Game.GRID_COLUMNS)] for _ in range(Game.GRID_ROWS)]
        
        self.snake: List[Vector2] = self.random_snake()
        self.grid_add_snake(self.snake[0])
        self.apple = self.random_apple()
        
        self.lives = 10
        self.score = 0
        self.is_over = False

        self.max_length = 0
        self.moves = 0
        #self.move_limit = 2*(Game.GRID_COLUMNS * Game.GRID_ROWS)**0.5
        #self.move_limit = 2*(Game.GRID_COLUMNS + Game.GRID_ROWS)
        self.move_limit = Game.GRID_COLUMNS * Game.GRID_ROWS / 2
    
    def reset(self):
        self.max_length = max(len(self.snake), self.max_length)
        self.moves = 0

        self.grid: Array2D[Cell] = [[Cell.EMPTY for _ in range(Game.GRID_COLUMNS)] for _ in range(Game.GRID_ROWS)]
        self.heatmap: Array2D[int] = [[0 for _ in range(Game.GRID_COLUMNS)] for _ in range(Game.GRID_ROWS)]

        self.snake: List[Vector2] = self.random_snake()
        self.apple = self.random_apple()
    
    def death(self):
        self.lives -= 1
        if self.lives > 0:
            self.reset()
        else:
            self.is_over = True

    def move(self, direction: Vector2):
        new_x = self.snake[0][0] + direction[0]
        new_y = self.snake[0][1] + direction[1]

        if not 0 <= new_x < Game.GRID_COLUMNS:
            self.score -= 2
            self.death()
        elif not 0 <= new_y < Game.GRID_ROWS:
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
        elif len(self.snake) + self.move_limit < self.moves:
            heatmap = np.array(self.heatmap).flatten()
            non_zero = np.where(heatmap != 0)[0]

            non_zero_heatmap = heatmap[non_zero]
            non_zero_penalty = (Game.GRID_SIZE - non_zero.size) / Game.GRID_SIZE

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
        
    def cell_to_screen(self, cell_position: Vector2) -> Vector2:
        return (cell_position[0] * self.cell_width, cell_position[1] * self.cell_height)
    
    def display_cell(self, position: Vector2, color: Vector3):
        screen_position = self.cell_to_screen(position)
        pygame.draw.rect(self.surface, color, (screen_position[0], screen_position[1], self.cell_width, self.cell_height))

    def display(self):
        # Background
        if not self.is_over:
            super().display()
        else:
            self.surface.fill(self.OVER_COLOR)

        # Grid lines
        pygame.draw.rect(self.surface, Game.LINE_COLOR, (0, 0, self.width-1, self.height-1), 2)

        # Snake
        for snake_cell in self.snake:
            self.display_cell(snake_cell, Game.SNAKE_BODY_COLOR)
        self.display_cell(self.snake[0], Game.SNAKE_HEAD_COLOR)
        
        # Apple
        self.display_cell(self.apple, Game.APPLE_COLOR)
