# source: http://stackoverflow.com/a/1557906/6009280

import atexit
from time import clock
from functools import reduce


def seconds_to_str(t):
    return "%d:%02d:%02d.%03d" % \
           reduce(lambda ll, b: divmod(ll[0], b) + ll[1:],
                  [(t * 1000,), 1000, 60, 60])


line = "=" * 40


def log(s, elapsed=None):
    print(line)
    print(seconds_to_str(clock()), '-', s)
    if elapsed:
        print("Elapsed time:", elapsed)
    print(line)
    print()


def endlog():
    end = clock()
    elapsed = end - start
    log("End Program", seconds_to_str(elapsed))


def now():
    return seconds_to_str(clock())


start = clock()
atexit.register(endlog)
log("Start Program")
