from deap import tools, creator, base
from game_code import capture
import random
import LearnBase

NUM_FEAT = len(LearnBase.LearnerBase.Features._fields)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("WeightVec", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

toolbox.register("attr_float", random.uniform, -1, 1)
toolbox.register("attr_pos_float", random.random)
toolbox.register("attr_neg_float", random.uniform, -1, 0)

toolbox.register("init_wv", tools.initRepeat, creator.WeightVec,
                 toolbox.attr_float, n=NUM_FEAT)


def create_seeded_ind(ind_init):
    ind = tools.initRepeat(list, toolbox.attr_pos_float, NUM_FEAT)
    # set indeces 0, 9, 10, 12, 13, 14 to negative, as they're bad
    bad_indeces = [0, 9, 10, 11, 12, 13]
    for i in bad_indeces:
        ind[i] = -1 * ind[i]  # change them to negative of themselves
    return ind_init(ind)


# create a population with some "seeded" individuals (pre-determined signs)
def initPopulation(pcls, ind_init, n_seed, n_rand):
    pop = [create_seeded_ind(ind_init) for i in range(n_seed)]
    rand_pop = [toolbox.init_wv() for i in range(n_rand)]
    pcls(pop + rand_pop)


N_SEEDED = 10
N_RAND = 10
POP = 20

# to train together, pass in just 1 weight vector, to train apart, pass in 2

toolbox.register("seeded_pop", initPopulation, list, creator.WeightVec, N_SEEDED, N_RAND)
toolbox.register("pop", tools.initRepeat, list, creator.WeightVec, n=POP)
