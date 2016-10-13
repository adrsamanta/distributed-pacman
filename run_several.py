import subprocess
from datetime import datetime

import argparse

today_folder = '{:%m.%d}'.format(datetime.now())

program = "python -m scoop GeneticLearner.py -ngen 16 -s 10 -r 5"
prefix = "OEL/" + today_folder + "/"

parser = argparse.ArgumentParser()

parser.add_argument("num_rounds", type=int)
parser.add_argument("--start_val", "-sv", type=int, default=0)


args = parser.parse_args()
rounds = args.num_rounds
start = args.sv

for i in range(start, start + rounds):
    outfile = open(prefix + str(i) + "out.log", "w")
    errfile = open(prefix + str(i) + "err.log", "w")
    subprocess.call(program, stdout=outfile, stderr=errfile, shell=True)
    print "finished call", i

print "done"
