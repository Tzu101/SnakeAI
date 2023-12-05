from classes.util import *


WeightInit = Callable[[int], List[float]]
BiasInit = Callable[[int], float]
NeuronInit = Callable[[], Tuple[WeightInit, BiasInit]]
ActivationFunction = Callable[[List[float]], List[float]]


class Neuron:

    def __init__(self, input_size: int, init_weight: WeightInit, init_bias: BiasInit):
        self.weights = init_weight(input_size)
        self.bias = init_bias(input_size)
    
    def compute(self, inputs: List[float]) -> float:
        value = self.bias
        for w in range(len(self.weights)):
            value += self.weights[w] * inputs[w]
        return value


class Layer:
    def __init__(self, size: int, input_size: int, init_function: NeuronInit, activation: ActivationFunction):
        self.size = size
        self.activation = activation

        """self.neurons: List[Neuron] = []
        for _ in range(self.size):
            neuron = Neuron(input_size, *init_function())
            self.neurons.append(neuron)"""
        
        self.weights: Array2D[float] = []
        self.biases: List[float] = []
        for _ in range(self.size):
            self.weights.append(init_function()[0](input_size))
            self.biases.append(init_function()[1](input_size))
    
    def compute(self, inputs: List[float]) -> List[float]:
        """values: list[float] = []
        for neuron in self.neurons:
            value = neuron.compute(inputs)
            values.append(value)"""

        values: list[float] = []
        for n in range(self.size):
            values.append(0)
            for w in range(len(self.weights[n])):
                values[n] += self.weights[n][w] * inputs[w]
            values[n] += self.biases[n]

        values = self.activation(values)
        return values


class Network:
    @staticmethod
    def initZero():
        def initZeroWeights(size: int) -> List[float]:
            return [0 for _ in range(size)]
        
        def initZeroBias(size: int):
            return 0
        
        return initZeroWeights, initZeroBias
        
    @staticmethod
    def initAbsRand():
        def initRandWeights(size: int):
            return [random.random() for _ in range(size)]
        
        def initRandBias(size: int):
            size_sqrt = size**0.5
            return random.random() * size_sqrt / 2
        
        return initRandWeights, initRandBias
    
    @staticmethod
    def initNegRand():
        def initRandWeights(size: int):
            return [random.random() * 2 - 1 for _ in range(size)]
        
        def initRandBias(size: int):
            size_sqrt = size**0.5
            return (random.random() - 0.5) * size_sqrt
        
        return initRandWeights, initRandBias

    @staticmethod
    def sigmoid(values: List[float]) -> List[float]:
        new_values: List[float] = []
        for value in values:
            new_values.append(1 / (1 + math.exp(-value)))
        return new_values

    @staticmethod
    def relu(values: List[float]) -> List[float]:
        new_values: List[float] = []
        for value in values:
            new_values.append(max(0, value))
        return new_values
    
    @staticmethod
    def tanh(values: List[float]) -> List[float]:
        new_values: List[float] = []
        for value in values:
            new_values.append(math.tanh(value))
        return new_values
    
    @staticmethod
    def softmax(values: List[float]) -> List[float]:
        max_value = max(values)

        exp_values: List[float] = []
        exp_sum = 0
        for value in values:
            exp_value = math.exp(value - max_value)
            exp_values.append(exp_value)
            exp_sum += exp_value

        new_values: List[float] = []
        for exp_value in exp_values:
            new_values.append(exp_value / exp_sum)
        return new_values

    @staticmethod
    def none(values: List[float]) -> List[float]:
        return values

    def __init__(self, input_size):
        self.input_size = input_size
        self.layers: List[Layer] = []
        self.outputs: List[float] = []
    
    def layer(self, size: int, init: NeuronInit, activation: ActivationFunction):
        input_size = self.input_size if len(self.layers) == 0 else self.layers[-1].size
        layer = Layer(size, input_size, init, activation)
        self.layers.append(layer)

    def compute(self, inputs: List[float]):
        for layer in self.layers:
            inputs = layer.compute(inputs)
        self.outputs = inputs

        return self.outputs.copy()


LayerActivation = Callable[[np.ndarray], np.ndarray]
LayerInit = Callable[..., np.ndarray]

class NeuralNetwork:

    @staticmethod
    def sigmoid(values: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-values))

    @staticmethod
    def relu(values: np.ndarray) -> np.ndarray:
        return np.maximum(0, values)
    
    @staticmethod
    def tanh(values: np.ndarray) -> np.ndarray:
        return np.tanh(values)
    
    @staticmethod
    def softmax(values: np.ndarray) -> np.ndarray:
        exp_values = np.exp(values - np.max(values, axis=-1, keepdims=True))
        return exp_values / np.sum(exp_values, axis=-1, keepdims=True)

    @staticmethod
    def none(values: np.ndarray) -> np.ndarray:
        return values
    

    class Layer:

        def __init__(self, size: int, input_size: int, activation: LayerActivation, init: LayerInit):
            self.size: int = size
            self.activation: LayerActivation = activation

            self.biases: np.ndarray = init(size)
            self.weights: np.ndarray = init(size, input_size)
        
        def compute(self, input: np.ndarray) -> np.ndarray:
            return np.dot(self.weights, input) + self.biases


    def __init__(self, size: int):
        self.input_size = size
        self.layers: List[NeuralNetwork.Layer] = []
    
    def layer(self, size: int, activation: LayerActivation, init: LayerInit=np.random.randn):
        input_size = self.input_size if len(self.layers) == 0 else self.layers[-1].size
        self.layers.append(NeuralNetwork.Layer(size, input_size, activation, init))

    def compute(self, input: np.ndarray):
        output = np.copy(input)
        for layer in self.layers:
            output = layer.compute(output)
        return output


NetworkConstructor = Callable[[], NeuralNetwork]
ScoreFunction = Callable[[np.ndarray, np.ndarray], float]


class GeneticAlgorithm:
    @staticmethod
    def absolute_error(results: np.ndarray, expected_output: np.ndarray) -> float:
        return np.sum(np.abs(expected_output - results))

    @staticmethod
    def crossover(network: NeuralNetwork, *parent_networks: NeuralNetwork):
        parent_chance = 1 / len(parent_networks)

        for l in range(len(network.layers)):
            layer = network.layers[l]

            for n in range(layer.size):
                parent_index = math.floor(random.random() // parent_chance)
                layer.biases[n] = parent_networks[parent_index].layers[l].biases[n]

                for w in range(len(layer.weights[n])):
                    parent_index = math.floor(random.random() // parent_chance)
                    layer.weights[n][w] = parent_networks[parent_index].layers[l].weights[n][w]

            """for n in range(len(layer.neurons)):
                neuron = layer.neurons[n]

                parent_index = math.floor(random.random() // parent_chance)
                neuron.bias = parent_networks[parent_index].layers[l].neurons[n].bias

                for w in range(len(neuron.weights)):
                    parent_index = math.floor(random.random() // parent_chance)
                    neuron.weights[w] = parent_networks[parent_index].layers[l].neurons[n].weights[w]"""

        return network
    
    @staticmethod
    def mutation(network: NeuralNetwork, chance: float):
        bias_clamp = network.input_size**0.5
        for l in range(len(network.layers)):
            layer = network.layers[l]

            for n in range(layer.size):
                if random.random() < chance:
                    layer.biases[n] = max(min(layer.biases[n] + random.random() - 0.5, bias_clamp), -bias_clamp)

                for w in range(len(layer.weights[n])):
                    if random.random() < chance:
                        layer.weights[n][w] = math.tanh(layer.weights[n][w] + random.random() - 0.5)

            """for n in range(len(layer.neurons)):
                neuron = layer.neurons[n]

                if random.random() < chance:
                    neuron.bias = max(min(neuron.bias + random.random() - 0.5, bias_clamp), -bias_clamp)

                for w in range(len(neuron.weights)):
                    if random.random() < chance:
                        neuron.weights[w] = math.tanh(neuron.weights[w] + random.random() - 0.5)"""
            bias_clamp = layer.size**0.5

        return network
    
    def __init__(self, population_size: int, survival_size: int, iteration_count: int, parent_count: int, mutation_chance: float, network_constructor: NetworkConstructor):
        self.population_size = population_size
        self.survival_size = survival_size
        self.iteration_count = iteration_count
        self.parent_count = parent_count
        self.mutation_chance = mutation_chance
        self.network_constructor = network_constructor
    
    def prepare_population(self) -> List[NeuralNetwork]:
        population = []
        for _ in range(self.population_size):
            population.append(self.network_constructor())
        return population
    
    def train(self, inputs: np.ndarray, expected_outputs: np.ndarray, score_function: ScoreFunction, score_ascending: bool = True) -> Union[NeuralNetwork, None]:
        population = self.prepare_population()
        best_agent = None

        for _ in range(self.iteration_count):
            scores: List[float] = []

            for agent in population:
                score = 0
                for i in range(len(inputs)):
                    result = agent.compute(inputs[i])
                    score += score_function(result, expected_outputs[i])
                scores.append(score)

            sorted_score_indices = np.argsort(np.array(scores))
            sorted_agents = np.array(population)[sorted_score_indices]

            if score_ascending:
                survivors = sorted_agents[:self.survival_size]
                best_agent = survivors[0]
            else:
                survivors = sorted_agents[-self.survival_size:]
                best_agent = survivors[-1]

            new_generation = []
            for _ in range(self.population_size - self.survival_size):
                new_agent = self.network_constructor()
                new_generation.append(new_agent)

                parent_agents: List[NeuralNetwork] = []
                for _ in range(self.parent_count):
                    parent_agents.append(survivors[random.randint(0, self.survival_size-1)])

                GeneticAlgorithm.crossover(new_agent, *parent_agents)    
                GeneticAlgorithm.mutation(new_agent, self.mutation_chance)
            population = [*survivors, *new_generation]
    
        return best_agent
