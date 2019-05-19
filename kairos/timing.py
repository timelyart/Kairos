# source: http://stackoverflow.com/a/1557906/6009280
import atexit
from time import time, strftime, localtime
from kairos import tools


def seconds_to_str(elapsed=None):
    if elapsed is None:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())
    else:
        return tools.display_time(elapsed)


def log(s, elapsed=None):
    line = "="*40
    print()
    print(line)
    print(seconds_to_str(), '-', s)
    if elapsed:
        print("Elapsed time:", elapsed)
    print(line)
    print()


def end_log():
    end = time()
    elapsed = end - start
    log("End Program", seconds_to_str(round(elapsed, 3)))


start = time()
atexit.register(end_log)
log("Start Program")
