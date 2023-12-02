import pygame
import random
from typing import List, Tuple, Union


"""
    CONSTANTS
"""
FPS = 60
GAME_WIDTH = 800
GAME_HEIGHT = 800
PANEL_HEIGHT = 100

SCREEN_WIDTH = GAME_WIDTH
SCREEN_HEIGHT = GAME_HEIGHT + PANEL_HEIGHT

GRID_COLUMNS = 10
GRID_ROWS = 10
GRID_WIDTH = 2

CELL_WIDTH = GAME_WIDTH // GRID_COLUMNS
CELL_HEIGHT = GAME_HEIGHT // GRID_ROWS

PANEL_COLOR = (175, 175, 185)
BACKGROUND_COLOR = (45, 45, 50)
LINE_COLOR = (0, 0, 0)
SNAKE_COLOR = (20, 150, 20)
APPLE_COLOR = (180, 40, 20)

"""
    UTILITY TYPES
"""

Vector2 = Tuple[int, int]
Vector3 = Tuple[int, int, int]
Event = Union[pygame.event.EventType, pygame.event.Event]

"""
    UTILITY CLASSES
"""

class Snake:

    body: List[Vector2] = []

    def __init__(self, start_pos: Vector2):
        self.body.append(start_pos)
    
    def move(self, move: Vector2):
        grid_x = self.body[0][0] + move[0]
        grid_y = self.body[0][1] + move[1]

        if grid_x < 0:
            grid_x += GRID_COLUMNS
        if grid_x >= GRID_COLUMNS:
            grid_x -= GRID_COLUMNS

        if grid_y < 0:
            grid_y += GRID_ROWS
        if grid_y >= GRID_ROWS:
            grid_y -= GRID_ROWS
        
        if grid.cells[grid_y][grid_x] == grid.EMPTY_CELL:

            next_cell = (grid_x, grid_y)
            grid.cells[grid_y][grid_x] = grid.SNAKE_CELL
            grid.cells[snake.body[-1][1]][snake.body[-1][0]] = grid.EMPTY_CELL
                
            for s in range(len(snake.body)):
                snake.body[s], next_cell = next_cell, snake.body[s]
            
            if grid.apple == snake.body[0]:
                grid.cells[next_cell[1]][next_cell[0]] = grid.SNAKE_CELL
                snake.body.append(next_cell)
                grid.get_new_apple()
        else:
            print("Dead")
    
    def input(self, event: Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.move((0, -1))
            elif event.key == pygame.K_s:
                self.move((0, 1))
            elif event.key == pygame.K_a:
                self.move((-1, 0))
            elif event.key == pygame.K_d:
                self.move((1, 0))
    
    def display(self):
        for body_cell in snake.body:
            cell_position = (body_cell[0] * CELL_WIDTH + GRID_WIDTH, body_cell[1] * CELL_HEIGHT + GRID_WIDTH + PANEL_HEIGHT)
            display_cell(cell_position, SNAKE_COLOR)

class Grid:
    EMPTY_CELL = 0
    SNAKE_CELL = 1

    debug: bool = False
    show_lines: bool = True
    cells: List[List[int]]
    cell_size: Vector2 = (CELL_WIDTH - GRID_WIDTH, CELL_HEIGHT - GRID_WIDTH)
    apple: Union[None, Vector2] = None

    def __init__(self):
        self.cells = [[0 for _ in range(GRID_COLUMNS)] for _ in range(GRID_ROWS)]
        self.get_new_apple()
    
    def get_new_apple(self):
        self.apple = (random.randint(0, GRID_COLUMNS-1), random.randint(0, GRID_ROWS-1))
        while self.apple in snake.body:
            self.apple = (random.randint(0, GRID_COLUMNS-1), random.randint(0, GRID_ROWS-1))

    def set_lines(self, are_lines: bool):
        self.show_lines = are_lines
        if (are_lines):
            self.cell_size: Vector2 = (CELL_WIDTH - GRID_WIDTH, CELL_HEIGHT - GRID_WIDTH)
        else:
            self.cell_size: Vector2 = (CELL_WIDTH, CELL_HEIGHT)
    
    def display(self):
        if self.apple:
            display_cell((self.apple[0] * CELL_WIDTH + GRID_WIDTH, self.apple[1] * CELL_HEIGHT + GRID_WIDTH + PANEL_HEIGHT), APPLE_COLOR)

        if self.debug:
            for row in range(GRID_ROWS):
                for col in range(GRID_COLUMNS):
                    if self.cells[row][col] == grid.SNAKE_CELL:
                        pygame.draw.rect(screen, "green", (col*CELL_WIDTH + CELL_WIDTH//4, row*CELL_HEIGHT + CELL_HEIGHT//4 + PANEL_HEIGHT, CELL_WIDTH//2, CELL_HEIGHT//2))   

        if self.show_lines:
            for row in range(GRID_ROWS):
                for col in range(GRID_COLUMNS):
                    row_end =  (row + 1) * CELL_HEIGHT + PANEL_HEIGHT
                    col_end = (col + 1) * CELL_WIDTH
                    pygame.draw.line(screen, LINE_COLOR, (0, row_end), (col_end, row_end), GRID_WIDTH)
                    pygame.draw.line(screen, LINE_COLOR, (col_end, PANEL_HEIGHT), (col_end, row_end), GRID_WIDTH)
            pygame.draw.rect(screen, LINE_COLOR, (0, PANEL_HEIGHT, SCREEN_WIDTH-1, GAME_HEIGHT-1), GRID_WIDTH)

"""
    UTILITY FUNCTIONS
"""

def inputs():
    global running

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        snake.input(event)
        
    

def display_cell(position: Vector2, color: Vector3):
    pygame.draw.rect(screen, color, (position[0], position[1], grid.cell_size[0], grid.cell_size[1]))    

def display():
    global screen

    # Background
    screen.fill(BACKGROUND_COLOR)

    # Panel
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, SCREEN_WIDTH, PANEL_HEIGHT))
        
    # Snake
    snake.display()

    # Grid
    grid.display()

    # Render
    pygame.display.flip()

"""
    GLOBALS VARIABLES
"""

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
delta_time = 0

gridLines = True

snake: Snake = Snake((GRID_COLUMNS // 2, GRID_ROWS // 2))
grid: Grid = Grid()

while running:
    inputs()
    display()
    
    delta_time = clock.tick(FPS) / 1000

pygame.quit()
