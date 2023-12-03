import time
import random
from classes.util import *
from classes.window import Window
from classes.network import Network, GeneticAlgorithm


if __name__ == "__main__":
    random.seed(time.time())

    def make_network():
        network = Network(2)
        network.layer(4, Network.initRand, Network.sigmoid)
        network.layer(2, Network.initRand, Network.softmax)
        return network

    train_inputs: Array2D[float] = [[0, 1], [1, 0]]
    train_outputs: Array2D[float] = [[1, 0], [0, 1]]
    gen_alg = GeneticAlgorithm(100, 10, 10, 2, 0.01, make_network)
    gen_alg.train(train_inputs, train_outputs, GeneticAlgorithm.absolute_error)

    # window = Window()
    # window.run()
