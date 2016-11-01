from __future__ import print_function
import argparse
import os
import pickle
from deap import tools, creator
from GeneticClasses import Team, Fitness0
from game_code import capture
import random


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

# bestScore = tools.selBest(scoreAgents, 1)[0]
# bestOffense = tools.selBest(offenseAgents, 1)[0]
# bestDefense = tools.selBest(defenseAgents, 1)[0]


def run_game(score, offe, defe, red_gen=True, blue_gen=True):
    if red_gen:
        red_team = ["-r", "GeneticAgent"]
        red_opts = ["--redOpts", "weightvec1=" + str(score.offense) + ";weightvec2=" + str(score.defense)]
    else:
        red_team = ["-r", "baselineTeam"]
        red_opts = []
    if blue_gen:
        blue_team = ["-b", "GeneticAgent"]
        blue_opts = ["--blueOpts", "weightvec1=" + str(offe.offense) + ";weightvec2=" + str(defe.defense)]
    else:
        blue_team = ["-b", "baselineTeam"]
        blue_opts = []

    game_opts = ["-c", "-l", "tinyCapture"]

    if not args.watch:
        game_opts.extend(["-q", "-n", "3"])

    score_food_list = capture.main_run(red_team + blue_team + red_opts + blue_opts + game_opts)
    labels = ["score", "food eaten", "enemy food eaten"]

    for sfl in score_food_list:
        print("Score: ", sfl[0])
        print("Red Food: ", sfl[1][0] + sfl[1][2])
        print("Blue Food: ", sfl[1][1] + sfl[1][3])

    # return the average score over all games
    return sum(sfl[0] for sfl in score_food_list) / len(score_food_list)


def make_team(offe, defe):
    return creator.ScoreTeam(offe.offense, defe.defense)


rounds = 10
score_scores = 0
composed_scores = 0
for i in range(rounds):
    score = random.choice(scoreAgents)
    score_scores += run_game(score, None, None, blue_gen=False)
    print("\ncomposed\n")
    offe = random.choice(offenseAgents)
    defe = random.choice(defenseAgents)
    composed_scores += run_game(make_team(offe, defe), None, None, blue_gen=False)
    print('\n\n')

print("Average score team score: ", score_scores / rounds)
print("Average composed score: ", composed_scores / rounds)

    # run_game(bestScore, bestOffense, bestDefense, True, True)
