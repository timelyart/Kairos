# File: debug.py
import logging
import sys
from selenium.common.exceptions import InvalidArgumentException, WebDriverException

log_path = './log'  # project dir
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


def load_console_log(browser, log_type):
    try:
        return browser.get_log(log_type)
    except InvalidArgumentException:
        return None
    except WebDriverException:
        return None


def write_console_log(browser, clear_on_startup=True):
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

    if not os.path.exists(log_path):
        os.mkdir(log_path)

    offset = tools.get_time_offset()
    for log_name in logs:
        if logs[log_name]:
            file = os.path.join(r"" + log_path, str(log_name) + ".log")
            if clear_on_startup:
                with open(file, 'w'):
                    pass
            f = open(file, 'a')
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
