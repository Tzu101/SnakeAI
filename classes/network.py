from classes.util import *


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
    def leaky_relu(values: np.ndarray) -> np.ndarray:
        return np.maximum(0.1*values, values)
    
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
        parent_networks_length = len(parent_networks)
        parent_chance = 1 / parent_networks_length

        for l in range(len(network.layers)):
            layer = network.layers[l]

            parent_biases = []
            for parent_network in parent_networks:
                parent_biases.append(parent_network.layers[l].biases)
            parent_biases = np.array(parent_biases)

            rand_bias_indices = np.random.choice(np.arange(parent_networks_length), size=layer.biases.size)
            layer.biases = np.where(rand_bias_indices, *parent_biases)

            for n in range(layer.size):
                parent_weights = []
                for parent_network in parent_networks:
                    parent_weights.append(parent_network.layers[l].weights[n])
                parent_weights = np.array(parent_weights)

                rand_weight_indices = np.random.choice(np.arange(parent_networks_length), size=layer.weights[n].size)
                layer.weights[n] = np.where(rand_weight_indices, *parent_weights)

                for w in range(len(layer.weights[n])):
                    parent_index = math.floor(random.random() // parent_chance)
                    layer.weights[n][w] = parent_networks[parent_index].layers[l].weights[n][w]

        return network
    
    @staticmethod
    def mutation(network: NeuralNetwork, chance: float):
        bias_clamp = network.input_size**0.5
        for l in range(len(network.layers)):
            layer = network.layers[l]

            mutated_bias_indices = np.where(np.random.choice(2, layer.biases.size, p=[1-chance, chance]) == 1)[0]
            layer.biases[mutated_bias_indices] += np.random.uniform(low=-1, high=1, size=mutated_bias_indices.size)
            layer.biases[mutated_bias_indices] = np.clip(layer.biases[mutated_bias_indices], -bias_clamp, bias_clamp)

            for n in range(layer.size):
                mutated_weight_indices = np.where(np.random.choice(2, layer.weights[n].size, p=[1-chance, chance]) == 1)[0]
                layer.weights[n][mutated_weight_indices] += np.random.uniform(low=-0.5, high=0.5, size=mutated_weight_indices.size)
                layer.weights[n][mutated_weight_indices] = np.tanh(layer.weights[n][mutated_weight_indices])

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
