import subprocess
from datetime import datetime

import argparse

today_folder = '{:%m.%d}'.format(datetime.now())

program = "python -m scoop GeneticLearner.py -ngen 16 -s 10 -r 5"
prefix = "OEL/" + today_folder + "/"

parser = argparse.ArgumentParser()

parser.add_argument("num_rounds", type=int)

args = parser.parse_args()
rounds = args.num_rounds
for i in range(rounds):
    outfile = open(prefix + str(i) + "out.log", "w")
    errfile = open(prefix + str(i) + "err.log", "w")
    subprocess.call(program, stdout=outfile, stderr=errfile, shell=True)
    print "finished call", i

print "done"
