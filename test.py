import time
import random
from classes.util import *
from classes.network import Network, GeneticAlgorithm


# Testing the neural network genetic algorithm
if __name__ == "__main__":
    random.seed(time.time())

    def make_network():
        network = Network(2)
        network.layer(4, Network.initAbsRand, Network.none)
        network.layer(1, Network.initAbsRand, Network.none)
        return network

    train_inputs: Array2D[float] = []
    train_outputs: Array2D[float] = []

    for t in range(100):
        x = random.randint(0, 9)
        y = random.randint(0, 9)
        train_inputs.append([x, y])
        train_outputs.append([x + y])

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
            print("Result: ", best_agent.compute([num1, num2]), "\n")
