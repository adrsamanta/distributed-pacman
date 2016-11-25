import os
import pickle

import numpy
from deap import tools, creator, base, algorithms
from GeneticClasses import Team, Fitness0

server = "server1"
subdir = "complex_pop_logbook"
# finaldir = "\\logs\\pop_logbook"
finaldir = ""
os.chdir(
    "C:\\Users\\alan.Blackbird\\Desktop\\Documents\\CS 6366\\distributed-pacman\\downloaded_logs\\" + server + "\\" + subdir + finaldir)

p = os.getcwd()
# weight structure:
# (score_weight, Amt of food eaten by offensive agent, amt of food eaten by enemy)
creator.create("ScoreMax", Fitness0, weights=(1.0, 0.0, 0.0))
# teams optimized with below fitnesses will only care about how well the offensive or defensive agent does
# so when picking best offensive/defensive agents, just pick best teams with these fitnesses
creator.create("AteFoodMax", Fitness0, weights=(0., 1., 0.))
creator.create("EFoodMin", Fitness0, weights=(0., 0., -1.))

creator.create("ScoreTeam", Team, fitness=creator.ScoreMax, type="Score")
creator.create("OffenseTeam", Team, fitness=creator.AteFoodMax, type="Offense")
creator.create("DefenseTeam", Team, fitness=creator.EFoodMin, type="Defense")

scoreAgents = []
offenseAgents = []
defenseAgents = []
allScore = []
files = os.listdir(p)


def process_file(file):
    global scoreAgents, offenseAgents, defenseAgents, allScore
    if file.endswith("pop.txt"):
        with open(file) as ifile:
            pop = pickle.load(ifile)
            allScore += pop
            best2 = tools.selBest(pop, 2)
            # best2 = pop
            type = best2[0].type
            if type == "Score":
                scoreAgents += best2
            elif type == "Offense":
                offenseAgents += best2
            elif type == "Defense":
                defenseAgents += best2
            else:
                print "unknown type: ", type


for file in files:
    process_file(file)

if "Offense" in files:
    os.chdir(p + "\\Offense")
    for file in os.listdir(os.getcwd()):
        process_file(file)

if "Defense" in files:
    os.chdir(p + "\\Defense")
    for file in os.listdir(os.getcwd()):
        process_file(file)


stats = tools.Statistics(key=lambda ind: ind.fitness.values)
stats.register("avg", numpy.mean, axis=0)
stats.register("std", numpy.std, axis=0)
stats.register("min", numpy.min, axis=0)
stats.register("max", numpy.max, axis=0)
stats.register('median', numpy.median, axis=0)

def pickle_all(filebase):
    os.chdir("C:\\Users\\alan.Blackbird\\Desktop\\Documents\\CS 6366\\distributed-pacman\\compiled_pops")
    with open(filebase + "_score", "w") as out:
        pickle.dump(scoreAgents, out)
    with open(filebase + "_offense", "w") as out:
        pickle.dump(offenseAgents, out)
    with open(filebase + "_defense", "w") as out:
        pickle.dump(defenseAgents, out)


def getFitness(agent):
    if agent.type == "Score":
        return agent.fitness.getValues()[0]
    if agent.type == "Offense":
        return agent.fitness.getValues()[1]
    if agent.type == "Defense":
        return agent.fitness.getValues()[2]


def countAbove(agents, floor):
    return sum(1 for a in agents if getFitness(a) >= floor)

def pickle_set(filebase, subset):
    os.chdir("C:\\Users\\alan.Blackbird\\Desktop\\Documents\\CS 6366\\distributed-pacman\\compiled_pops")
    with open(filebase + "_" + subset[0].type.lower(), "w") as out:
        pickle.dump(subset, out)
