from classes.util import *
from classes.abstract import Controler
from classes.network import NeuralNetwork


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

    def __init__(self, network: NeuralNetwork):
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

        wall_up = snake_y
        snake_up = 10
        for y in range(snake_y, 0, -1):
            if grid[y-1][snake_x] == Cell.EMPTY:
                snake_up -= 1
            else:
                snake_up = -snake_up
                break
        snake_up = max(snake_up, 0)
        
        apple_up = 10
        if apple_y < snake_y:
            apple_up = snake_y - apple_y

        wall_down = grid_height - snake_y - 1
        snake_down = 10
        for y in range(snake_y, grid_height-1):
            if grid[y+1][snake_x] == Cell.EMPTY:
                snake_down -= 1
            else:
                snake_down = -snake_down
                break
        snake_down = max(snake_down, 0)

        apple_down = 10
        if apple_y > snake_y:
            apple_down = apple_y - snake_y
        
        wall_left = snake_x
        snake_left = 10

        for x in range(snake_x, 0, -1):
            if grid[snake_y][x-1] == Cell.EMPTY:
                snake_left -= 1
            else:
                snake_left = -snake_left
                break
        snake_left = max(snake_left, 0)

        apple_left = 10
        if apple_x < snake_x:
            apple_left = snake_x - apple_x

        wall_right = grid_width - snake_x - 1
        snake_right = 10
        for x in range(snake_x, grid_width-1):
            if grid[snake_y][x+1] == Cell.EMPTY:
                snake_right -= 1
            else:
                snake_right = -snake_right
                break
        snake_right = max(snake_right, 0)

        apple_right = 10
        if apple_x > snake_x:
            apple_right = apple_x - snake_x

        neural_input: List[float] = [
            wall_up, wall_down, wall_left, wall_right, 
            snake_up, snake_down, snake_left, snake_right, 
            apple_up, apple_down, apple_left, apple_right,
        ]

        """neural_input: List[float] = []
        for y in range(grid_height):
            for x in range(grid_width):
                if grid[y][x] == Cell.FULL:
                    neural_input.append(1)
                else:
                    neural_input.append(0)
        
        snake_x_bin = [0 for _ in range(grid_width)]
        snake_x_bin[snake_x] = 1

        snake_y_bin = [0 for _ in range(grid_height)]
        snake_y_bin[snake_y] = 1

        apple_x_bin = [0 for _ in range(grid_width)]
        apple_x_bin[apple_x] = 1

        apple_y_bin = [0 for _ in range(grid_height)]
        apple_y_bin[apple_y] = 1

        neural_input = [*neural_input, *snake_x_bin, *snake_y_bin, *apple_x_bin, *apple_y_bin]"""
        
        """danger_up = 0
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
        ]"""
        
        output = self.network.compute(np.array(neural_input))
        action_index = np.argmax(output)

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