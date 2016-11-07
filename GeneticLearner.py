from datetime import datetime
import numpy
from deap import tools, creator, base, algorithms
from game_code import capture
import random
import LearnBase
import argparse
import os
from scoop import futures
from pympler import tracker, summary, muppy
from GeneticClasses import Team, Fitness0
import pickle

# stime = '{:%m-%d_%H.%M.%S}'.format(datetime.now())
# olog = open("logs/outlogs/" + stime + "_outlog.txt", "w", buffering=0)


def log(msg):
    print msg
    # olog.write(msg + "\n")


parser = argparse.ArgumentParser()

parser.add_argument("-ngen", type=int, default=100)
parser.add_argument("--seed", "-s", type=int, required=True)
parser.add_argument("--rand", "-r", type=int, required=True)
parser.add_argument("-cxpb", type=float, default=.5)
parser.add_argument("-mutpb", type=float, default=.5)
parser.add_argument("-indpb", type=float, default=.4)
parser.add_argument("-d", action="store_true")
parser.add_argument("--pop_file", "-pf", type=file)
parser.add_argument("--pop_out", "-po", type=str)
parser.add_argument("--type", "-t", choices=["s", "o", 'd'], default="s", type=str)
parser.add_argument("--enemy_hid", "-eh", action='store_true')
parser.add_argument("--layout", "-l", type=str, default="")

args = parser.parse_args()
NUM_FEAT = len(LearnBase.LearnerBase.Features._fields)

N_SEEDED = args.seed  # number of seeded individuals in population at start
N_RAND = args.rand  # number of randomly generated individuals in population
POP = N_SEEDED + N_RAND  # number of individuals in the total pop

NGEN = args.ngen  # number of generations
CXPB = args.cxpb  # crossover probability
MUTPB = args.mutpb  # mutation probability
INDPB = args.indpb  # probability of mutating a given feature



debug = args.d

toolbox = base.Toolbox()




# weight structure:
# (score_weight, Amt of food eaten by offensive agent, amt of food eaten by enemy)
creator.create("ScoreMax", Fitness0, weights=(1.0, 0.0, 0.0))
# teams optimized with below fitnesses will only care about how well the offensive or defensive agent does
# so when picking best offensive/defensive agents, just pick best teams with these fitnesses
creator.create("AteFoodMax", Fitness0, weights=(0., 1., 0.))
creator.create("EFoodMin", Fitness0, weights=(0., 0., -1.))

# TODO: add seeded or unseeded flag
creator.create("ScoreTeam", Team, fitness=creator.ScoreMax, type="Score")
creator.create("OffenseTeam", Team, fitness=creator.AteFoodMax, type="Offense")
creator.create("DefenseTeam", Team, fitness=creator.EFoodMin, type="Defense")



if __name__ == '__main__':
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


if __name__ == '__main__':
    toolbox.register("create_score_team", create_same_team, team=creator.ScoreTeam)
    toolbox.register("create_offense_team", create_same_team, team=creator.OffenseTeam)
    toolbox.register("create_defense_team", create_same_team, team=creator.DefenseTeam)


# create a population with some "seeded" individuals (pre-determined signs)
def initPopulation(pcls, team, n_seed, n_rand):
    pop = [team(True) for i in range(n_seed)]
    rand_pop = [team(False) for i in range(n_rand)]
    return pcls(pop + rand_pop)


if __name__ == '__main__':
    # pops for score team
    if args.type == "s":
        team = toolbox.create_score_team
        print "score team"
    elif args.type == "o":
        team = toolbox.create_offense_team
        print "offense team"
    elif args.type == "d":
        team = toolbox.create_defense_team
        print "defense team"
    toolbox.register("seeded_pop", initPopulation, list, team, N_SEEDED, N_RAND)
    toolbox.register("pop", initPopulation, list, team, 0, POP)


def evaluate(indiv):
    # if my team is red, will ALWAYS be indeces 0, 2. Also: weightvecs are assigned to agents in order
    # so offensive agent is at index 0
    ltime = '{:%m-%d_%H.%M.%S}'.format(datetime.now())
    red_team = ["-r", "GeneticAgent"]
    # blue_team = ["-b", "baselineTeam"]  # will play against baseline for now, can change later
    blue_team = ["-b", "HLANoPlan"]
    red_opts = ["--redOpts", "weightvec1=" + str(indiv.offense) + ";weightvec2=" + str(indiv.defense)]
    if args.layout:
        # have a layout
        layout = args.layout
    else:
        layout = "tinyCapture"
    game_opts = ["-q", "-c", "-l", layout, "-n", "3"]
    if not args.enemy_hid:
        game_opts.append("-v")
    # no graphics, because no one there to watch! also catch exceptions
    log("starting games at " + ltime + " on " + str(os.getpid()))
    score_food_list = capture.main_run(red_team + blue_team + red_opts + game_opts)
    log("ending games started at " + ltime + " on " + str(os.getpid()))
    # find the average values of these over all games
    score = sum(s[0] for s in score_food_list) / len(score_food_list)  # avg score over all games
    off_food = sum(s[1][0] for s in score_food_list) / len(score_food_list)
    e_food = sum(s[1][1] + s[1][3] for s in score_food_list) / len(score_food_list)

    # assuming 4 agents, 0 is offensive, 2 is defensive, 1, 3 are enemies
    return score, off_food, e_food


# apply a crossover algorithm to the 2 individuals
def apply_cx(ind1, ind2, cx):
    cx(ind1.offense, ind2.offense)
    cx(ind1.defense, ind2.defense)

    return ind1, ind2


# apply a mutation algorithm to the individual
def apply_mut(ind1, mut):
    mut(ind1.offense)
    mut(ind1.defense)
    return (ind1,)


if __name__ == '__main__':
    toolbox.register("cxblend", tools.cxBlend, alpha=.5)
    toolbox.register("mutgauss", tools.mutGaussian, mu=0, sigma=.5, indpb=INDPB)

    toolbox.register("mate", apply_cx, cx=toolbox.cxblend)
    toolbox.register("mutate", apply_mut, mut=toolbox.mutgauss)
    toolbox.register("select", tools.selBest)


def fake_eval(indiv):
    return -10 * random.random(), 10, 10


if __name__ == '__main__':

    if debug:
        toolbox.register("evaluate", fake_eval)
    else:
        toolbox.register("evaluate", evaluate)

    pop_file = args.pop_file
    if pop_file:
        pop = pickle.load(pop_file)
    else:
        pop = toolbox.seeded_pop()


def doEval(individuals):
    invalid_ind = [ind for ind in individuals if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    # efn = timestamp+"_error.txt"
    # sys.stderr = open(efn, "w")


if __name__ == '__main__':
    memtrack = False
    stats = tools.Statistics(key=lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)

    logbook = tools.Logbook()
    if memtrack:
        all_obj = muppy.get_objects()
        sumStart = summary.summarize(all_obj)
        summary.print_(sumStart)
        all_obj = None
        sumStart = None
        tr = tracker.SummaryTracker()

    # pool = multiprocessing.Pool()
    # toolbox.register("map", pool.map)
    toolbox.register("map", futures.map)

    log("beginning initial evaluation")
    # do initial evaluation:
    doEval(pop)

    logbook.record(gen=-1, **stats.compile(pop))
    log("starting iteration")
    for g in range(NGEN):
        log("\n\nstarting generation " + str(g) + "\n\n")
        breeder_len = int(.8 * len(pop))
        keep_len = len(pop) - breeder_len
        keepers = tools.selBest(pop, keep_len)
        # copy the breeders
        # breeders=toolbox.map(toolbox.clone, toolbox.select(pop, breeder_len)) (not needed b/c of varAnd)
        z = toolbox.select(pop, breeder_len)
        offspring = algorithms.varAnd(toolbox.select(pop, breeder_len), toolbox, CXPB, MUTPB)

        doEval(offspring)

        pop = keepers + offspring
        logbook.record(gen=g, **stats.compile(pop))
        if memtrack:
            tr.print_diff()
        record = stats.compile(pop)
        for k, v in record.iteritems():
            print k, v
    log("cleanup")
    print "logbook length ", len(logbook)
    prefix = "logs/intelligent_agent_pl/"
    if args.type == "o":
        prefix += "Offense/"
    elif args.type == "d":
        prefix += "Defense/"
    timestamp = '{:%m-%d_%H.%M.%S}'.format(datetime.now())
    log_file_name = prefix + timestamp + "_log.txt"
    pop_file_name = prefix + timestamp + "_pop.txt"

    with open(log_file_name, "w") as log_file:
        pickle.dump(logbook, log_file)

    with open(pop_file_name, "w") as pop_file:
        pickle.dump(pop, pop_file)

    if args.pop_out:
        with open(args.pop_out, "w") as pop_out:
            pickle.dump(pop, pop_out)

    record = stats.compile(pop)
    for k, v in record.iteritems():
        print k, v

    print "DONE"

