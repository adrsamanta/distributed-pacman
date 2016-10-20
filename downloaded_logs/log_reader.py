import os
import pickle
from deap import tools, creator, base, algorithms
from GeneticClasses import Team, Fitness0

server = "server1"

os.chdir(
    "C:\\Users\\alan.Blackbird\\Desktop\\Documents\\CS 6366\\distributed-pacman\\downloaded_logs\\" + server + "\\logs\\pop_logbook")

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

files = os.listdir(p)

for file in files:
    if file.endswith("pop.txt"):
        with open(file) as ifile:
            pop = pickle.load(ifile)
            best2 = tools.selBest(pop, 2)
            type = best2[0].type
            if type == "Score":
                scoreAgents += best2
            elif type == "Offense":
                offenseAgents += best2
            elif type == "Defense":
                defenseAgents += best2
            else:
                print "unknown type: ", type
