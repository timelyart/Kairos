# File: debug.py
import logging
import os
import re
import sys

from datetime import datetime

import coloredlogs

file_name = 'debug.log'
log_path = os.path.join('.', 'log')
if not os.path.exists(log_path):
    os.mkdir(log_path)


def create_log(mode='a', level=logging.DEBUG):
    file = os.path.join(r"" + log_path, file_name)
    # noinspection PyArgumentList
    log_format = '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s'
    date_format = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(file, mode=mode),
            logging.StreamHandler(sys.stdout)
        ])
    logger = logging.getLogger()
    coloredlogs.install(level=level, logger=logger, fmt=log_format, datefmt=date_format)
    return logger, coloredlogs


def shutdown_logging():
    logging.shutdown()


# noinspection PyBroadException
def load_console_log(browser, log_type):
    try:
        return browser.get_log(log_type)
    except Exception:
        return None


def write_console_log(browser, mode='a'):
    import os
    from kairos import tools
    from datetime import datetime
    from datetime import timedelta

    logs = {
        'browser': load_console_log(browser, 'browser'),
        'driver': load_console_log(browser, 'driver'),
        'server': load_console_log(browser, 'server'),
        'client': load_console_log(browser, 'client'),
        'performance': load_console_log(browser, 'performance')
    }

    postfix = ""
    match = re.search(r".*(/d+)", file_name)
    if match:
        postfix = "_".format(match.group(1))

    offset = tools.get_time_offset()
    for log_name in logs:
        if logs[log_name]:
            fn = "{}{}.log".format(str(log_name), postfix)
            file = os.path.join(r"" + log_path, fn)
            f = open(file, mode)
            lines = logs[log_name]
            for line in lines:
                level = line['level']
                message = line['message']
                timestamp = datetime(1970, 1, 1, ) + timedelta(microseconds=line['timestamp']*1000) + offset
                s_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                # apparently, the webdriver adds a carriage return ('\r') after each entry but no line feed ('\n')
                output = "{} {} \t {} \n".format(s_timestamp, level, message)
                f.write(output)
            f.close()


def log(level, method, msg):
    t = datetime.now()
    ms = t.strftime("%f")[:3]
    print("{}.{}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ms), level, method, msg)
