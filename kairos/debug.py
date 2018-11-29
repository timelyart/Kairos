# File: debug.py
import logging
import sys

log_path = '.'  # project dir
file_name = 'debug.log'


# empty the content of the file
def clear_log():
    with open(file_name, 'w'):
        pass


def create_log():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("{0}/{1}".format(log_path, file_name)),
            logging.StreamHandler(sys.stdout)
        ])
    return logging.getLogger()
