import random
import numpy


class Perceptron(object):
    """A single perceptron."""
    def output_processor(self, x):
        return 0 if x < 0 else 1

    def initial_weight(self, x):
        """Function that defines the initial weight of index `x` of the
        network."""
        return random.random()

    def __init__(self, input_size, eta=0.2):
        self.weights = numpy.fromfunction(self.initial_weight, input_size)

        self.errors = []
        self.eta = eta

        self.fitness = 0.0

        self.plot = plugincon.easy_bot_command("gt_plotall", True)(self.plot)

    def think(self, inputs):
        """Activates the perceptron network."""
        result = numpy.dot(inputs, self.weights)
        error = self.fitness - self.output_processor(result)
        self.fitness = fitness
        self.errors.append(error)

        return result

    def score(self, fitness):
        """How well the machine has performed."""
        self.fitness = fitness

class Sigmoid(Perceptron):
    def output_processor(self, x):
        return 1 / (1 + 2.71828182846**-x)

class Thinker(object):
    """A network of Perceptrons."""
    def __init__(self, input_size, output_size, eta=0.2, node_type=Perceptron):
        self.eta = eta

        if hasattr(nodetype, "__iter__"):
            self.perceptrons = [node_type[min(i, len(node_type) - 1)](input_size, eta) for i in xrange(output_size)]

        else:
            self.perceptrons = [node_type(input_size, eta) for _ in xrange(output_size)]

    def think(self, inputs):
        """Activates the network."""
        return [x.think(inputs) for x in self.perceptrons]

    def score(self, fitness):
        """Gives a global score to all perceptrons in the network."""
        for x in self.perceptrons:
            x.score(fitness)

    def separate_scoring(self, fitnesses):
        """Gives a separate scoring for each perceptron, in a list."""
        for p, f in zip(self.perceptrons, fitnesses):
            p.score(f)

    def resize(self, input_size, output_size):
        weights = [x.weights for x in self.perceptrons]

        self.perceptrons = [Perceptron(input_size, self.eta) for _ in xrange(output_size)]

        for p, w in zip(self.perceptrons, weights):
            p.weights = w

class FunctionThinker(Thinker):
    def __init__(self, input_size, output_size, eta=0.2, node_type=Perceptron, functions=None):
        Thinker.__init__(self, input_size, output_size, eta, node_type)

        self.functions = functions

    def think_and_act(self, inputs, functions=True, call_condition=lambda other, x: x >= 0):
        if type(functions) is bool:
            if functions:
                functions = self.functions

            else:
                functions = None

        elif hasattr(functions, "__call__"):
            functions = [functions] * len(self.perceptrons)

        for o, f in zip(self.think(inputs), functions):
            if call_condition(self, o):
                f(self, o)
