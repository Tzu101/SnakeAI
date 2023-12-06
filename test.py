from classes.util import *
from classes.network import GeneticAlgorithm, NeuralNetwork


# Testing the neural network genetic algorithm
if __name__ == "__main__":

    """def mutation1(values: np.ndarray, chance: float):
        for v in range(values.size):
            if np.random.rand() < chance:
                values[v] = np.random.rand()
        return values

    def mutation2(values: np.ndarray, chance: float):
        size = values.size
        mutate_count = random_round(size * chance)

        mutated_bias_indices = np.random.choice(size, mutate_count, replace=False)
        values[mutated_bias_indices] += np.random.uniform(low=-0.5, high=0.5, size=mutate_count)

        return values
    
    v1 = np.zeros(10)
    v2 = np.zeros(10)
    print(mutation1(v1, 0.1))
    print(mutation2(v2, 0.1))"""
    
    my_array = np.arange(50).reshape((10, 5))
    indices_of_top_5 = np.argsort(my_array.flatten())
    print(indices_of_top_5)
    print(indices_of_top_5[-5:])

    """apple_x = 1
    apple_y = 1

    pos_x = 0
    pos_y = 0

    fov = 4
    full_grid = -1 * np.ones((10 + 2*fov, 10 + 2*fov), dtype=int)
    snake_grid = np.arange(100)
    snake_grid = np.reshape(snake_grid, (10, 10))
    full_grid[fov:10+fov, fov:10+fov] = snake_grid
    fov_grid = full_grid[pos_y:pos_y+2*fov+1, pos_x:pos_x+2*fov+1]

    while True:
        last_value = fov_grid[fov + apple_y - pos_y][fov + apple_x - pos_x]
        if abs(apple_y - pos_y) <= fov and abs(apple_x - pos_x) <= fov:
            fov_grid[fov + apple_y - pos_y][fov + apple_x - pos_x] = 111
        print(full_grid[pos_y:pos_y+2*fov+1, pos_x:pos_x+2*fov+1])
        fov_grid[fov + apple_y - pos_y][fov + apple_x - pos_x] = last_value

        user_input = input("Move awsd:\n")

        if user_input.lower() == 'a':
            pos_x -= 1
        if user_input.lower() == 'w':
            pos_y -= 1
        if user_input.lower() == 's':
            pos_y += 1
        if user_input.lower() == 'd':
            pos_x += 1
        if user_input.lower() == "":
            break"""
    
    """def make_network():
        network = NeuralNetwork(2)
        network.layer(4, NeuralNetwork.sigmoid)
        network.layer(1, NeuralNetwork.none)
        return network

    train_inputs = np.random.randint(0, 10, size=(1000, 2))
    train_outputs = np.sum(train_inputs, axis=1)

    gen_alg = GeneticAlgorithm(100, 10, 10, 2, 0.1, make_network)
    best_agent = gen_alg.train(train_inputs, train_outputs, GeneticAlgorithm.absolute_error)

    if best_agent:
        while True:
            user_input = input("Enter two numbers seperated by a space:\n")

            if user_input.lower() == '':
                break
            
            user_input = user_input.split(" ")
            if len(user_input) != 2:
                print("Error: Input should be two numbers seperated by a space!\n")
                continue

            if not user_input[0].isdigit() or not user_input[1].isdigit():
                print("Error: Input should be valid numbers!\n")
                continue

            num1 = float(user_input[0])
            num2 = float(user_input[1])
            print("Result: ", best_agent.compute(np.array([num1, num2])), "\n")"""
