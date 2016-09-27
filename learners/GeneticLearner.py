from deap import tools, creator, base
from game_code import capture
import random
import LearnBase

NUM_FEAT = len(LearnBase.LearnerBase.Features._fields)


class Team(object):
    def __init__(self, off, defe):
        self.offense = off
        self.defense = defe


# weight structure:
# (score_weight, Amt of food eaten by offensive agent, amt of food eaten by enemy)

creator.create("ScoreMax", base.Fitness, weights=(1.0, 0.0, 0.0))
# teams optimized with below fitnesses will only care about how well the offensive or defensive agent does
# so when picking best offensive/defensive agents, just pick best teams with these fitnesses
creator.create("AteFoodMax", base.Fitness, weights=(0., 1., 0.))
creator.create("EFoodMin", base.Fitness, weights=(0., 0., -1.))

creator.create("ScoreTeam", Team, fitness=creator.ScoreMax)
creator.create("OffenseTeam", Team, fitness=creator.AteFoodMax)
creator.create("DefenseTeam", Team, fitness=creator.EFoodMin)

toolbox = base.Toolbox()

toolbox.register("attr_float", random.uniform, -1, 1)
toolbox.register("attr_pos_float", random.random)
toolbox.register("attr_neg_float", random.uniform, -1, 0)

toolbox.register("init_wv", tools.initRepeat, list,
                 toolbox.attr_float, n=NUM_FEAT)

def create_seeded_ind(ind_init):
    ind = tools.initRepeat(list, toolbox.attr_pos_float, NUM_FEAT)
    # set indeces 0, 9, 10, 12, 13, 14 to negative, as they're bad
    bad_indeces = [0, 9, 10, 11, 12, 13]
    for i in bad_indeces:
        ind[i] = -1 * ind[i]  # change them to negative of themselves
    return ind_init(ind)


# should agent 1 be seeded, should agent 2 be seeded, what team are we using

def create_same_team(seed, team):
    return create_team(seed, seed, team)


def create_team(seeded1, seeded2, team):
    if seeded1:
        off = create_seeded_ind(list)
    else:
        off = toolbox.init_wv()

    if seeded2:
        defe = create_seeded_ind(list)
    else:
        defe = toolbox.init_wv()

    return team(off, defe)


toolbox.register("create_score_team", create_same_team, team=creator.ScoreTeam)
toolbox.register("create_offense_team", create_same_team, team=creator.OffenseTeam)
toolbox.register("create_defense_team", create_same_team, team=creator.DefenseTeam)

# create a population with some "seeded" individuals (pre-determined signs)
def initPopulation(pcls, team, n_seed, n_rand):
    pop = [team(True) for i in range(n_seed)]
    rand_pop = [team(False) for i in range(n_rand)]
    pcls(pop + rand_pop)



N_SEEDED = 10
N_RAND = 10
POP = 20

# pops for score team
toolbox.register("seeded_pop", initPopulation, list, toolbox.create_score_team, N_SEEDED, N_RAND)
toolbox.register("pop", initPopulation, list, toolbox.create_score_team, 0, POP)


def evaluate(indiv):
    # if my team is red, will ALWAYS be indeces 0, 2. Also: weightvecs are assigned to agents in order
    # so offensive agent is at index 0
    red_team = ["-r", "GeneticAgent"]
    blue_team = ["-b", "baselineTeam"]  # will play against baseline for now, can change later

    red_opts = ["--redOpts", "weightvec1=" + str(indiv.offense), "weightvec2=" + str(indiv.defense)]

    game_opts = ["-q"]  # no graphics, because no one there to watch!
    score_food_list = capture.main_run(red_team + blue_team + red_opts)

    # find the average values of these over all games
    score = sum(s[0] for s in score_food_list) / len(score_food_list)  # avg score over all games
    off_food = sum(s[1][0] for s in score_food_list) / len(score_food_list)
    e_food = sum(s[1][1] + s[1][3] for s in score_food_list) / len(score_food_list)

    # assuming 4 agents, 0 is offensive, 2 is defensive, 1, 3 are enemies
    return score, off_food, e_food


    # create function that takes in a mutation function, applies it to both vectors in the team, so can define
    # toolbox.mutate functions via it, just call toolbox.mutate(indiv)
    # also can create multiple mutations easily

    # Do above for crossover as well
    # does crossover between agent types occur or not?


    # for selection, select the best 90%, mutate them amongst each other, keep the best 10% from previous gen unchanged (is that too high?)
