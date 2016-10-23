import argparse
import os
import pickle
from deap import tools, creator
from GeneticClasses import Team, Fitness0
from game_code import capture

os.chdir("./compiled_pops")

parser = argparse.ArgumentParser()
parser.add_argument("score_file", type=file, help="file of score teams")
parser.add_argument("offense_file", type=file, help="file of offensive agents")
parser.add_argument("defense_file", type=file, help="file of defensive agents")
parser.add_argument("--watch", "-w", action="store_true")

args = parser.parse_args()

# (score_weight, Amt of food eaten by offensive agent, amt of food eaten by enemy)
creator.create("ScoreMax", Fitness0, weights=(1.0, 0.0, 0.0))
# teams optimized with below fitnesses will only care about how well the offensive or defensive agent does
# so when picking best offensive/defensive agents, just pick best teams with these fitnesses
creator.create("AteFoodMax", Fitness0, weights=(0., 1., 0.))
creator.create("EFoodMin", Fitness0, weights=(0., 0., -1.))

creator.create("ScoreTeam", Team, fitness=creator.ScoreMax, type="Score")
creator.create("OffenseTeam", Team, fitness=creator.AteFoodMax, type="Offense")
creator.create("DefenseTeam", Team, fitness=creator.EFoodMin, type="Defense")

scoreAgents = pickle.load(args.score_file)
offenseAgents = pickle.load(args.offense_file)
defenseAgents = pickle.load(args.defense_file)

# modify as needed

bestScore = tools.selBest(scoreAgents, 1)
bestOffense = tools.selBest(offenseAgents, 1)
bestDefense = tools.selBest(defenseAgents, 1)


def run_game(score, offe, defe):
    red_team = ["-r", "GeneticAgent"]
    blue_team = ["-b", "GeneticAgent"]

    red_opts = ["--redOpts", "weightvec1=" + str(score.offense) + ";weightvec2=" + str(score.defense)]
    blue_opts = ["--blueOpts", "weightvec1=" + str(offe.offense) + ";weightvec2=" + str(defe.defense)]
    game_opts = ["-c", "-l", "tinyCapture"]

    if not args.watch:
        game_opts.extend(["-q", "-n", "3"])

    score_food_list = capture.main_run(red_team + blue_team + red_opts + blue_opts + game_opts)
    labels = ["score", "food eaten", "enemy food eaten"]
    for v, l in zip(score_food_list, labels):
        print v, l


run_game(bestScore, bestOffense, bestDefense)
