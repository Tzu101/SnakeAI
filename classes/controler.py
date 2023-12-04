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
        self.last_action = Action.NONE
        self.network = network
    
    def compute_action(self, grid: Array2D[Cell], snake: List[Vector2], apple: Vector2) -> Action:

        grid_width = len(grid[0])
        grid_height = len(grid)

        snake_x = snake[0][0]
        snake_y = snake[0][1]
        #snake_length = len(snake)

        apple_x = apple[0]
        apple_y = apple[1]

        #manhattan_distance = float(abs(apple_x - snake_x) + abs(apple_y - snake_y))

        """space_up = 0
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
        
        neural_input: List[float] = [snake_x, snake_y, space_up, space_down, space_left, space_right, apple_x, apple_y]"""

        """neural_input: List[float] = []
        for y in range(grid_height):
            pos_y = snake_y + y - grid_height // 2
            for x in range(grid_width):
                pos_x = snake_x + x - grid_width // 2

                if (not 0 <= pos_y < grid_height or
                    not 0 <= pos_x < grid_width):
                    neural_input.append(-1)
                elif grid[pos_y][pos_x] == Cell.FULL:
                    neural_input.append(-1)
                elif pos_y == apple_y and pos_x == apple_x:
                    neural_input.append(1)
                else:
                    neural_input.append(0)"""
        
        danger_up = 0
        if snake_y < 0 or grid[snake_y-1][snake_x] == Cell.FULL:
            danger_up = 1

        danger_down = 0
        if snake_y >= grid_height-1 or grid[snake_y+1][snake_x] == Cell.FULL:
            danger_down = 1

        danger_left = 0
        if snake_x < 0 or grid[snake_y][snake_x-1] == Cell.FULL:
            danger_left = 1
        
        danger_right = 0
        if snake_x >= grid_width-1 or grid[snake_y][snake_x+1] == Cell.FULL:
            danger_right = 1
        
        apple_up = 0
        apple_down = 0
        if apple_y - snake_y < 0:
            apple_up = 1
        elif apple_y - snake_y > 0:
            apple_down = 1

        apple_left = 0
        apple_right = 0
        if apple_x - snake_x < 0:
            apple_left = 1
        elif apple_x - snake_x > 0:
            apple_right = 1
        
        last_up = 0
        last_down = 0
        last_left = 0
        last_right = 0

        if self.last_action == Action.UP:
            last_up = 1
        elif self.last_action == Action.DOWN:
            last_down = 1
        elif self.last_action == Action.LEFT:
            last_left = 1
        elif self.last_action == Action.RIGHT:
            last_right = 1

        neural_input: List[float] = [
            danger_up, danger_down, danger_left, danger_right, 
            apple_up, apple_down, apple_left, apple_right, 
            last_up, last_down, last_left, last_right
        ]
        

        output = self.network.compute(neural_input)
        action_index = output.index(max(output))

        action = Action.NONE
        if action_index == 0:
            action =  Action.UP
        if action_index == 1:
            action =  Action.DOWN
        if action_index == 2:
            action =  Action.LEFT
        if action_index == 3:
            action = Action.RIGHT
        
        self.last_action = action
        return action