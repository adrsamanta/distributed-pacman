import time
import sys

ox = open("outfile1.txt", "a")

for i in range(100):
    ox.write("output\n")
    print "output"
    ox.flush()
    sys.stdout.flush()
    time.sleep(1)

ox.close()
