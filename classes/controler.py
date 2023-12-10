from classes.util import *
from classes.abstract import Controler
from classes.network import NeuralNetwork


class DummyControler(Controler):
    def __init__(self):
        super().__init__()


class ManualControler(Controler):

    def __init__(self):
        super().__init__()
        self.valid_action = Action.NONE
        self.key_queue: List[Key] = []
        self.key_queue_length = 0

    def key_queue_add(self, new_key: Key):
        if new_key not in self.key_queue:
            self.key_queue.append(new_key)
            self.key_queue_length += 1

    def key_queue_remove(self, old_key: Key):
        if old_key in self.key_queue:
            self.key_queue.remove(old_key)
            self.key_queue_length -= 1

    def compute_action(self, grid: Array2D[Cell], snake: List[Vector2], apple: Vector2) -> Action:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.key_queue_add(Key.UP)
        else:
            self.key_queue_remove(Key.UP)

        if keys[pygame.K_s]:
            self.key_queue_add(Key.DOWN)
        else:
            self.key_queue_remove(Key.DOWN)

        if keys[pygame.K_a]:
            self.key_queue_add(Key.LEFT)
        else:
            self.key_queue_remove(Key.LEFT)

        if keys[pygame.K_d]:
            self.key_queue_add(Key.RIGHT)
        else:
            self.key_queue_remove(Key.RIGHT)

        self.action = Action.NONE
        if self.key_queue_length <= 0:
            return self.action

        is_snake_short = len(snake) == 1
        if self.key_queue[0] == Key.UP:
            if is_snake_short or not self.valid_action == Action.DOWN:
                self.action = Action.UP
                self.valid_action = Action.UP

        elif self.key_queue[0] == Key.DOWN:
            if is_snake_short or not self.valid_action == Action.UP:
                self.action = Action.DOWN
                self.valid_action = Action.DOWN   

        elif self.key_queue[0] == Key.LEFT:
            if is_snake_short or not self.valid_action == Action.RIGHT:
                self.action = Action.LEFT
                self.valid_action = Action.LEFT 

        elif self.key_queue[0] == Key.RIGHT:
            if is_snake_short or not self.valid_action == Action.LEFT:
                self.action = Action.RIGHT
                self.valid_action = Action.RIGHT 
        
        return self.action
    

NeuralInput = Union[List[float], np.ndarray]
InputCalculator = Callable[[Array2D[Cell], List[Vector2], Vector2, Action], NeuralInput]

class NeuralControler(Controler):

    @staticmethod
    def binary_network() -> NeuralNetwork:
        network = NeuralNetwork(12)
        network.layer(8, NeuralNetwork.tanh)
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
    def numeric_network() -> NeuralNetwork:
        network = NeuralNetwork(24)
        network.layer(10, NeuralNetwork.tanh)
        network.layer(4, NeuralNetwork.none)
        return network

    @staticmethod
    def numeric_input(grid: Array2D[Cell], snake: List[Vector2], apple: Vector2, action: Action) -> NeuralInput:
        # Params
        grid_width = len(grid[0])
        grid_height = len(grid)
        grid_avg_size = (grid_width + grid_height) / 2

        snake_x = snake[0][0]
        snake_y = snake[0][1]

        apple_x = apple[0]
        apple_y = apple[1]

        """
            Inputs
        """
        
        # Wall
        wall_up = snake_y
        wall_down = grid_height - snake_y - 1
        wall_left = snake_x
        wall_right = grid_width - snake_x - 1

        wall_up_left = min(wall_up, wall_left)
        wall_up_right = min(wall_up, wall_right)
        wall_down_left = min(wall_down, wall_left)
        wall_down_right = min(wall_down, wall_right)

        # Snake
        snake_up = grid_height
        snake_down = grid_height
        snake_left = grid_width
        snake_right = grid_width

        snake_up_left = grid_avg_size
        snake_up_right = grid_avg_size
        snake_down_left = grid_avg_size
        snake_down_right = grid_avg_size

        snake_head_x = snake[0][0]
        snake_head_y = snake[0][1]
        for snake_body in snake[1:]:
            temp_snake_up = grid_height
            temp_snake_down = grid_height
            temp_snake_left = grid_width
            temp_snake_right = grid_width

            temp_snake_up_left = grid_avg_size
            temp_snake_up_right = grid_avg_size
            temp_snake_down_left = grid_avg_size
            temp_snake_down_right = grid_avg_size

            snake_body_x = snake_body[0]
            snake_body_y = snake_body[1]

            dist_x = abs(snake_head_x - snake_body_x)
            dist_y = abs(snake_head_y - snake_body_y)

            head_over_body_y = snake_head_y > snake_body_y
            body_over_head_y = snake_body_y > snake_head_y
            head_over_body_x = snake_head_x > snake_body_x
            body_over_head_x = snake_body_x > snake_head_x

            if dist_x == 0:
                if head_over_body_y:
                    temp_snake_up = dist_y - 1
                elif body_over_head_y:
                    temp_snake_down = -dist_y + 1

            if dist_y == 0:
                if head_over_body_x:
                    temp_snake_left = dist_x - 1
                elif body_over_head_x:
                    temp_snake_right = -dist_x + 1

            if dist_x == dist_y:
                if head_over_body_y and head_over_body_x:
                    temp_snake_up_left = dist_x
                elif head_over_body_y and body_over_head_x:
                    temp_snake_up_right = dist_x
                elif body_over_head_y and head_over_body_x:
                    temp_snake_down_left = dist_x
                elif body_over_head_y and body_over_head_x:
                    temp_snake_down_right = dist_x
            
            snake_up = min(snake_up, temp_snake_up)
            snake_down = min(snake_down, temp_snake_down)
            snake_left = min(snake_left, temp_snake_left)
            snake_right = min(snake_right, temp_snake_right)

            snake_up_left = min(snake_up_left, temp_snake_up_left)
            snake_up_right = min(snake_up_right, temp_snake_up_right)
            snake_down_left = min(snake_down_left, temp_snake_down_left)
            snake_down_right = min(snake_down_right, temp_snake_down_right)
        
        # Apple
        apple_up = grid_height
        apple_down = grid_height
        apple_left = grid_width
        apple_right = grid_width

        apple_x = apple[0]
        apple_y = apple[1]

        if apple_y < snake_head_y:
            apple_up = snake_head_y - apple_y - 1
        elif apple_y > snake_head_y:
            apple_down = apple_y - snake_head_y - 1

        if apple_x < snake_head_x:
            apple_left = snake_head_x - apple_x - 1
        elif apple_x > snake_head_x:
            apple_right = apple_x - snake_head_x - 1

        apple_up_left = (apple_up + apple_left) / 2
        apple_up_right = (apple_up + apple_right) / 2
        apple_down_left = (apple_down + apple_left) / 2
        apple_down_right = (apple_down + apple_right) / 2

        # Final
        neural_input = np.array([
            wall_up, wall_down, wall_left, wall_right,
            wall_up_left, wall_up_right, wall_down_left, wall_down_right,
            snake_up, snake_down, snake_left, snake_right,
            snake_up_left, snake_up_right, snake_down_left, snake_down_right,
            apple_up, apple_down, apple_left, apple_right,
            apple_up_left, apple_up_right, apple_down_left, apple_down_right,
        ])

        mean = np.mean(neural_input, axis=0)
        std_dev = np.std(neural_input, axis=0)

        # Standardize the data
        return (neural_input - mean) / std_dev
    
    @staticmethod
    def small_grid_network() -> NeuralNetwork:
        network = NeuralNetwork(13)
        network.layer(8, NeuralNetwork.tanh)
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
        network.layer(16, NeuralNetwork.tanh)
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