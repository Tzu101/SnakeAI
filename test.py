from classes.util import *
from classes.network import GeneticAlgorithm, NeuralNetwork


# Testing the neural network genetic algorithm
if __name__ == "__main__":
    def make_network():
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
            print("Result: ", best_agent.compute(np.array([num1, num2])), "\n")
