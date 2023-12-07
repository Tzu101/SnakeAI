from classes.util import *
from classes.abstract import Controler
from classes.network import NeuralNetwork


class ManualControler(Controler):

    def __init__(self):
        super().__init__()
        self.user_action = Action.NONE

    def compute_action(self, grid: Array2D[Cell], snake: List[Vector2], apple: Vector2) -> Action:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            if self.user_action == Action.DOWN:
                self.action = Action.NONE
            else:
                self.action = Action.UP
                self.user_action = Action.UP
        elif keys[pygame.K_s]:
            if self.user_action == Action.UP:
                self.action = Action.NONE
            else:
                self.action = Action.DOWN
                self.user_action = Action.DOWN
        elif keys[pygame.K_a]:
            if self.user_action == Action.RIGHT:
                self.action = Action.NONE
            else:
                self.action = Action.LEFT
                self.user_action = Action.LEFT
        elif keys[pygame.K_d]:
            if self.user_action == Action.LEFT:
                self.action = Action.NONE
            else:
                self.action = Action.RIGHT
                self.user_action = Action.RIGHT
        else:
            self.action = Action.NONE
        
        return self.action
    

NeuralInput = Union[List[float], np.ndarray]
InputCalculator = Callable[[Array2D[Cell], List[Vector2], Vector2, Action], NeuralInput]

class NeuralControler(Controler):

    @staticmethod
    def binary_network() -> NeuralNetwork:
        network = NeuralNetwork(12)
        network.layer(4, NeuralNetwork.tanh)
        network.layer(4, NeuralNetwork.none)
        return network

    @staticmethod
    def binary_input(grid: Array2D[Cell], snake: List[Vector2], apple: Vector2, action: Action) -> NeuralInput:
        # Params
        grid_width = len(grid[0])
        grid_height = len(grid)

        snake_x = snake[0][0]
        snake_y = snake[0][1]

        apple_x = apple[0]
        apple_y = apple[1]

        # Inputs
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

        if action == Action.UP:
            last_up = 1
        elif action == Action.DOWN:
            last_down = 1
        elif action == Action.LEFT:
            last_left = 1
        elif action == Action.RIGHT:
            last_right = 1

        return [
            danger_up, danger_down, danger_left, danger_right, 
            apple_up, apple_down, apple_left, apple_right, 
            last_up, last_down, last_left, last_right
        ]

    @staticmethod
    def range_network() -> NeuralNetwork:
        network = NeuralNetwork(12)
        network.layer(8, NeuralNetwork.leaky_relu)
        network.layer(4, NeuralNetwork.none)
        return network

    @staticmethod
    def range_input(grid: Array2D[Cell], snake: List[Vector2], apple: Vector2, action: Action) -> NeuralInput:
        # Params
        grid_width = len(grid[0])
        grid_height = len(grid)

        snake_x = snake[0][0]
        snake_y = snake[0][1]

        apple_x = apple[0]
        apple_y = apple[1]

        # Inputs
        wall_up = snake_y
        apple_up = grid_height
        if apple_y < snake_y:
            apple_up = snake_y - apple_y
        snake_up = grid_height
        for y in range(snake_y, 0, -1):
            if grid[y-1][snake_x] == Cell.EMPTY:
                snake_up -= 1
            else:
                snake_up = -snake_up
                break
        snake_up = max(snake_up, 0)

        wall_down = grid_height - snake_y - 1
        apple_down = grid_height
        if apple_y > snake_y:
            apple_down = apple_y - snake_y
        snake_down = grid_height
        for y in range(snake_y, grid_height-1):
            if grid[y+1][snake_x] == Cell.EMPTY:
                snake_down -= 1
            else:
                snake_down = -snake_down
                break
        snake_down = max(snake_down, 0)

        wall_left = snake_x
        apple_left = grid_width
        if apple_x < snake_x:
            apple_left = snake_x - apple_x
        snake_left = grid_width
        for x in range(snake_x, 0, -1):
            if grid[snake_y][x-1] == Cell.EMPTY:
                snake_left -= 1
            else:
                snake_left = -snake_left
                break
        snake_left = max(snake_left, 0)

        wall_right = grid_width - snake_x - 1
        apple_right = grid_width
        if apple_x > snake_x:
            apple_right = apple_x - snake_x
        snake_right = grid_width
        for x in range(snake_x, grid_width-1):
            if grid[snake_y][x+1] == Cell.EMPTY:
                snake_right -= 1
            else:
                snake_right = -snake_right
                break
        snake_right = max(snake_right, 0)

        return [
            wall_up, wall_down, wall_left, wall_right, 
            snake_up, snake_down, snake_left, snake_right, 
            apple_up, apple_down, apple_left, apple_right,
        ]
    
    @staticmethod
    def small_grid_network() -> NeuralNetwork:
        network = NeuralNetwork(13)
        network.layer(8, NeuralNetwork.leaky_relu)
        network.layer(8, NeuralNetwork.leaky_relu)
        network.layer(4, NeuralNetwork.none)
        return network

    @staticmethod
    def small_grid_input(grid: Array2D[Cell], snake: List[Vector2], apple: Vector2, action: Action) -> NeuralInput:
        # Params
        grid_width = len(grid[0])
        grid_height = len(grid)

        snake_x = snake[0][0]
        snake_y = snake[0][1]

        apple_x = apple[0]
        apple_y = apple[1]

        # Inputs
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
        
        neural_input = np.array([apple_up, apple_down, apple_left, apple_right])
        
        fov = 1
        full_grid = -1 * np.ones((grid_height + 2*fov, grid_width + 2*fov), dtype=int)
        snake_grid = np.array(grid)
        full_grid[fov:grid_height+fov, fov:grid_width+fov] = snake_grid
        fov_grid = full_grid[snake_y:snake_y+2*fov+1, snake_x:snake_x+2*fov+1]

        if abs(apple_y - snake_y) <= fov and abs(apple_x - snake_x) <= fov:
            fov_grid[fov + apple_y - snake_y][fov + apple_x - snake_x] = 1

        return np.concatenate((neural_input, fov_grid.flatten()))
    
    @staticmethod
    def large_grid_network() -> NeuralNetwork:
        network = NeuralNetwork(53)
        network.layer(16, NeuralNetwork.leaky_relu)
        network.layer(16, NeuralNetwork.leaky_relu)
        network.layer(4, NeuralNetwork.none)
        return network

    @staticmethod
    def large_grid_input(grid: Array2D[Cell], snake: List[Vector2], apple: Vector2, action: Action) -> NeuralInput:
        # Params
        grid_width = len(grid[0])
        grid_height = len(grid)

        snake_x = snake[0][0]
        snake_y = snake[0][1]

        apple_x = apple[0]
        apple_y = apple[1]

        # Inputs
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
        
        neural_input = np.array([apple_up, apple_down, apple_left, apple_right])
        
        fov = 3
        full_grid = -1 * np.ones((grid_height + 2*fov, grid_width + 2*fov), dtype=int)
        snake_grid = np.array(grid)
        full_grid[fov:grid_height+fov, fov:grid_width+fov] = snake_grid
        fov_grid = full_grid[snake_y:snake_y+2*fov+1, snake_x:snake_x+2*fov+1]

        if abs(apple_y - snake_y) <= fov and abs(apple_x - snake_x) <= fov:
            fov_grid[fov + apple_y - snake_y][fov + apple_x - snake_x] = 1

        return np.concatenate((neural_input, fov_grid.flatten()))


    def __init__(self, network: NeuralNetwork, input_calculator: InputCalculator):
        super().__init__()
        self.network = network
        self.input_calculator = input_calculator
    
    def compute_action(self, grid: Array2D[Cell], snake: List[Vector2], apple: Vector2) -> Action:

        neural_input = self.input_calculator(grid, snake, apple, self.action)
        output = self.network.compute(np.array(neural_input))
        action_index = np.argmax(output)

        self.action = Action.NONE
        if action_index == 0:
            self.action =  Action.UP
        if action_index == 1:
            self.action =  Action.DOWN
        if action_index == 2:
            self.action =  Action.LEFT
        if action_index == 3:
            self.action = Action.RIGHT
        
        return self.action