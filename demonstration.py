from __future__ import print_function
import argparse
import os
import pickle
from deap import tools, creator
from GeneticClasses import Team, Fitness0
from game_code import capture
import numpy as np
import random

parser = argparse.ArgumentParser()
parser.add_argument("score_file", type=file, help="file of score teams")
parser.add_argument("offense_file", type=file, help="file of offensive agents")
parser.add_argument("defense_file", type=file, help="file of defensive agents")

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

bestScore = tools.selBest(scoreAgents, 1)[0]
bestOffense = tools.selBest(offenseAgents, 1)[0]
bestDefense = tools.selBest(defenseAgents, 1)[0]


def run_game(score, offe, defe, red_gen=True, blue_gen=True, newArgs=None):
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

    game_opts = ["-c", "-l", "tinyCapture", '-v']
    if newArgs:
        game_opts += newArgs
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


# print('score 1', bestScore.offense)
# print('score 2', bestScore.defense)
# print('best off', bestOffense.offense)
# print('best def', bestDefense.defense)


f1 = lambda: run_game(bestScore, bestOffense, bestDefense, True, True, ['-i', '60'])
f2 = lambda: run_game(bestScore, None, None, True, False, ['-i', '600'])
f3 = lambda: run_game(make_team(bestOffense, bestDefense), None, None, True, False, ['-i', '600'])

f4 = lambda: run_game(make_team(random.choice(offenseAgents), random.choice(defenseAgents)),
                      None, None, True, False, ['-i', '600'])


def replay():
    run_game(bestScore, bestOffense, bestDefense, True, False, ['-i', '1', '-q'])
    capture.main_run(['--replay', 'replay-score-good'])


# for sa in scoreAgents:
#     if run_game(sa, None, None, True, False, ['--record', '-i', '400', '-q'])==10:
#         print('worked!')
#         print('score 1', sa.offense)
#         print('score 2', sa.defense)
#         break



'''
score 1 [0.017576816625534578, 0.011354058833838443, -0.0011065192575554494, 0.24622804263634807, 0.8531796976315957, -0.0359265388337898, 0.45445017268537985, 1.3207227473392202, -0.4452379421997679, -0.7756701291366089, 1.5264227317414258, -0.05638947552824877, -0.822346155727489, -1.2921773123645146]
score 2 [0.30090541001540866, -0.2764355603659417, -2.035061362585868, 1.021242417111978, 0.6474561202811888, 0.7194452211744311, 0.6177495731308291, 0.6806354710286727, 0.6588150430352995, 0.43227953323566665, -0.9890587117013281, -2.141945333332475, -1.9542043737503965, -0.23567811268328592]
'''

# score 1 [-1.0247768257329408, -0.6438404601144798, 0.46177107415847723, -0.1565969346996826, 0.542314956533291, 0.8849483467259759, 0.6278018699090804, 0.6613062751767663, -0.35502964752067034, -0.16442424157354668, -0.7748659791640724, -0.3526127299370551, 0.48343473445696816, -2.780769037321739]
# score 2 [0.5009818237970682, -0.323441378858228, -0.7997086117315347, -0.13246812847562806, -0.36038115943238386, -1.54044909342356, -0.7889210960251399, 0.06818128146545688, -0.9221768644908868, 0.867643642539468, 0.34825023999772, -0.7357848215345567, -1.0976866089224915, -0.24631237610697743]


# funky results:
# [-0.6053409288136434, 0.3188127997745541, 1.2954801005576697, 0.39115924580088407, 0.5973587335317387, 0.1669410799109416, 0.35672657900454907, 0.676957481165485, 0.7490127741565753, -0.7629355057902121, -0.9475797363012826, -0.32839864166387767, -0.45122311515960956, -0.120248993408889
# [-0.06114530769494941, 0.9121924708454048, 0.41386983489611606, 0.18985212736873536, 0.042470825091085795, 0.39843025640439145, 0.07312524171835522, 0.5330406991664152, 0.8554553626358401, -0.7041050037523315, -0.9777096932855929, -0.0979015239394857, -0.7653317097093955, -0.1770000634617297]

# f3()
stats = tools.Statistics()
stats.register("avg", np.mean, axis=0)
stats.register("std", np.std, axis=0)
stats.register("min", np.min, axis=0)
stats.register("max", np.max, axis=0)
stats.register('median', np.median, axis=0)


def printFeatureStats():
    pass
