import subprocess

program = "python -m scoop GeneticLearner.py -ngen 16 -s 10 -r 5"
prefix = "OEL/10.12/"

for i in range(5):
    outfile = open(prefix + str(i) + "out.log", "w")
    errfile = open(prefix + str(i) + "err.log", "w")
    subprocess.call(program, stdout=outfile, stderr=errfile, shell=True)
    print "finished call", i

print "done"
