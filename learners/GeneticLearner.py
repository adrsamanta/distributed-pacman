from deap import tools, creator, base
from game_code import capture
import random
import LearnBase

NUM_FEAT = len(LearnBase.LearnerBase.Features._fields)

creator.create("FitnessMax", base.Fitness, weights=(1.0))
creator.create("WeightVec", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

toolbox.register("attr_float", random.random)
toolbox.register("weightvec", tools.initRepeat, creator.WeightVec,
                 toolbox.attr_float, n=NUM_FEAT)


# to train together, pass in just 1 weight vector, to train apart, pass in 2
