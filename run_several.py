import subprocess
from datetime import datetime

import argparse

today_folder = '{:%m.%d}'.format(datetime.now())

program = "python -m scoop GeneticLearner.py -ngen 18 -s 10 -r 5"
prefix = "OEL/" + today_folder + "/offense_"
# prefix = "OEL/lr2/"
parser = argparse.ArgumentParser()

parser.add_argument("num_rounds", type=int)
parser.add_argument("--start_val", "-sv", type=int, default=0)
parser.add_argument("--start_pop", "-sp", type=file)
parser.add_argument("--pipe_pop", "-p", action="store_true")
parser.add_argument("-d", action="store_true")
parser.add_argument("-ho", action="store_true")

args = parser.parse_args()
rounds = args.num_rounds
start = args.start_val

if args.d:
    program += " -d "

if args.ho:
    prefix = ""

if args.start_pop:
    print "not implemented yet you fool"

tmp_pop_file = "rs_tmp_pop.file"

if args.pipe_pop:
    program += " -po " + tmp_pop_file

for i in range(start, start + rounds):
    outfile = open(prefix + str(i) + "out.log", "w")
    errfile = open(prefix + str(i) + "err.log", "w")
    subprocess.call(program, stdout=outfile, stderr=errfile, shell=True)
    print "finished call", i
    if i == 0:
        # only after first call, start piping the pop
        program += " -pf " + tmp_pop_file

print "done"
