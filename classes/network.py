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

        self.neurons: List[Neuron] = []
        for _ in range(size):
            neuron = Neuron(input_size, *init_function())
            self.neurons.append(neuron)
    
    def compute(self, inputs: List[float]) -> List[float]:
        values: list[float] = []
        for neuron in self.neurons:
            value = neuron.compute(inputs)
            values.append(value)

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
    def initRand():
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


NetworkConstructor = Callable[[], Network]
ScoreFunction = Callable[[List[float], List[float]], float]


class GeneticAlgorithm:
    @staticmethod
    def absolute_error(results: List[float], expected_output: List[float]) -> float:
        error = 0
        for r in range(len(results)):
            error += abs(expected_output[r] - results[r])
        return error

    @staticmethod
    def crossover(network: Network, *parent_networks: Network):
        parent_chance = 1 / len(parent_networks)

        for l in range(len(network.layers)):
            layer = network.layers[l]

            for n in range(len(layer.neurons)):
                neuron = layer.neurons[n]

                parent_index = math.floor(random.random() // parent_chance)
                neuron.bias = parent_networks[parent_index].layers[l].neurons[n].bias

                for w in range(len(neuron.weights)):
                    parent_index = math.floor(random.random() // parent_chance)
                    neuron.weights[w] = parent_networks[parent_index].layers[l].neurons[n].weights[w]

        return network
    
    @staticmethod
    def mutation(network: Network, chance: float):
        for l in range(len(network.layers)):
            layer = network.layers[l]
            for n in range(len(layer.neurons)):
                neuron = layer.neurons[n]

                if random.random() < chance:
                    neuron.bias += random.random() - 0.5
                    #neuron.bias *= random.random() * 2

                for w in range(len(neuron.weights)):
                    if random.random() < chance:
                        neuron.weights[w] += random.random() - 0.5
                        #neuron.weights[w] *= random.random() * 2

        return network
    
    def __init__(self, population_size: int, survival_size: int, iteration_count: int, parent_count: int, mutation_chance: float, network_constructor: NetworkConstructor):
        self.population_size = population_size
        self.survival_size = survival_size
        self.iteration_count = iteration_count
        self.parent_count = parent_count
        self.mutation_chance = mutation_chance
        self.network_constructor = network_constructor
    
    def prepare_population(self) -> List[Network]:
        population = []
        for _ in range(self.population_size):
            population.append(self.network_constructor())
        return population
    
    def train(self, inputs: Array2D[float], expected_outputs: Array2D[float], score_function: ScoreFunction, score_ascending: bool = True) -> Union[Network, None]:
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

            agent_scores = list(zip(population, scores))
            sorted_agent_scores = sorted(agent_scores, key=lambda x: x[1])
            sorted_agents = [agent for agent, _ in sorted_agent_scores]

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

                parent_agents: List[Network] = []
                for _ in range(self.parent_count):
                    parent_agents.append(survivors[random.randint(0, self.survival_size-1)])

                GeneticAlgorithm.crossover(new_agent, *parent_agents)    
                GeneticAlgorithm.mutation(new_agent, self.mutation_chance)
            population = [*survivors, *new_generation]
    
        return best_agent
