from classes.util import *
from classes.abstract import Controler
from classes.network import Network


class ManualControler(Controler):

    def __init__(self):
        super().__init__()

    def compute_action(self, grid: Array2D[Cell], snake: List[Vector2], apple: Vector2) -> Action:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            return Action.UP
        if keys[pygame.K_s]:
            return Action.DOWN
        if keys[pygame.K_a]:
            return Action.LEFT
        if keys[pygame.K_d]:
            return Action.RIGHT
        
        return Action.NONE
    

class NeuralControler(Controler):

    def __init__(self, network: Network):
        super().__init__()
        self.network = network
    
    def compute_action(self, grid: Array2D[Cell], snake: List[Vector2], apple: Vector2) -> Action:

        grid_width = len(grid[0])
        grid_height = len(grid)

        snake_x = snake[0][0]
        snake_y = snake[0][1]
        snake_length = len(snake)

        apple_x = apple[0]
        apple_y = apple[1]

        #manhattan_distance = float(abs(apple_x - snake_x) + abs(apple_y - snake_y))

        space_up = 0
        for y in range(snake_y, 0, -1):
            if grid[y-1][snake_x] == Cell.EMPTY:
                space_up += 1
            else:
                break

        space_down = 0
        for y in range(snake_y, grid_height-1):
            if grid[y+1][snake_x] == Cell.EMPTY:
                space_down += 1
            else:
                break

        space_left = 0
        for x in range(snake_x, 0, -1):
            if grid[snake_y][x-1] == Cell.EMPTY:
                space_left += 1
            else:
                break

        space_right = 0
        for x in range(snake_x, grid_width-1):
            if grid[snake_y][x+1] == Cell.EMPTY:
                space_right += 1
            else:
                break
        
        neural_input: List[float] = [snake_x, snake_y, space_up, space_down, space_left, space_right, apple_x, apple_y]

        output = self.network.compute(neural_input)
        action = output.index(max(output))

        if action == 0:
            return Action.UP
        if action == 1:
            return Action.DOWN
        if action == 2:
            return Action.LEFT
        if action == 3:
            return Action.RIGHT
        
        return Action.NONE