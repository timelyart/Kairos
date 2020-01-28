import shutil
import sys
import os
import psutil
from kairos import debug

BATCHES = list()


def print_disclaimer():
    print("DISCLAIMER")
    print("This program is free software: you can redistribute it and/or modify")
    print("it under the terms of the GNU General Public License as published by")
    print("the Free Software Foundation, either version 3 of the License, or")
    print("(at your option) any later version.\n")
    print("This program is distributed in the hope that it will be useful,")
    print("but WITHOUT ANY WARRANTY; without even the implied warranty of")
    print("MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the")
    print("GNU General Public License for more details.\n")
    print("You should have received a copy of the GNU General Public License")
    print("along with this program. If not, see <http://www.gnu.org/licenses/>.\n\n")


def print_help():
    print("HELP")
    print("usage: python main.py [<file>] [-s|-s <minutes>] [-h] [-d]\n")
    print("<file>\t\t YAML file with alert definitions and/or summary option")
    print("-s\t\t Flag. Read your mailbox, create summary and send it to your mailbox. See kairos.cfg.")
    print("<minutes>\t Delay creating a summary for <number> of minutes (e.g. to allow alerts to get triggered first).")
    print("-cls\t\t Clean session data that is exclusively used by Kairos. Your browser's user data folder is left untouched by this action.")
    print("-sort\t\t Sort existing back testing results (json). Requires 3 parameters -sort <filename> <sort_by> <reverse>:")
    print("\t\t Example usage: output\\my_back_test_20190527_1048.json \"Net Profit %\" no")
    print("\t\t\t <filename>: the file to sort")
    print("\t\t\t <sort_by>: define on which value to sort (use quites). Accepted values are: \"Net Profit\", \"Net Profit %\", \"Closed Trades\", \"Percent Profitable\", \"Profit Factor\", \"Max Drawdown\", \"Max Drawdown %\", \"Avg Trade\", \"Avg Trade %\"")
    print("\t\t\t <reverse>: optional. Sort in ascending or descending order? Default is 'yes' (descending)")
    # print("-m\t\t Flag. Run in multiprocessing mode. This requires setting up Selenium Grid. More information can be found here: https://www.seleniumhq.org/docs/07_selenium_grid.jsp\n")
    print("-h\t\t Flag. Show this help.")
    print("-d\t\t Flag. Show disclaimer.\n")


def main():
    try:
        print_disclaimer()
        print("USAGE\npython main.py [<file>] [-s|-s <minutes>] [-h] [-d]")
        print("For help, type: python main.py -h\n")
        # test_mongodb()
        yaml = ""
        multi_threading = False
        send_summary = False
        delay_summary = 0
        i = 1
        while i < len(sys.argv):
            if str(sys.argv[i]).endswith('.yaml'):
                yaml = sys.argv[i]
            elif str(sys.argv[i]) == '-s':
                send_summary = True
            elif str(sys.argv[i]) == '-h':
                print_help()
            elif str(sys.argv[i]) == '-d':
                print_disclaimer()
            elif str(sys.argv[i]) == '-m':
                multi_threading = True
            elif i > 1 and str(sys.argv[(i-1)]) == '-s':
                delay_summary = int(sys.argv[i])
            elif str(sys.argv[i]) == '-cls':
                clean_browser_data()
            elif str(sys.argv[i]) == '-sort':
                if i+2 < len(sys.argv):
                    back_test_file = str(sys.argv[i+1])
                    sort_by = str(sys.argv[i+2])
                    reverse = True
                    if i+3 < len(sys.argv):
                        reverse = str(sys.argv[i+3]).casefold().startswith("y") or str(sys.argv[i+3]).casefold().startswith("t") or str(sys.argv[i+3]) == 1
                    sort_back_test_data(back_test_file, sort_by, reverse)
                break
            elif not str(sys.argv[i]).endswith('main.py'):
                print("No such argument: " + str(sys.argv[i]))
            i += 1

        triggered_signals = []
        # print(__name__)
        if len(yaml) > 0:
            # set log name before importing... the import creates the log whatever it's file name
            debug.file_name = os.path.basename(yaml) + '.log'
            from tv import tv
            send_signals_immediately = not send_summary
            triggered_signals = tv.run(yaml, send_signals_immediately, multi_threading)
        if send_summary:
            # set log name before importing... the import creates the log whatever it's file name
            debug.file_name = 'summary.log'
            if len(yaml) > 0:
                debug.file_name = os.path.basename(yaml) + '.log'
                from tv import mail
                mail.run(delay_summary, yaml, triggered_signals)
    except Exception as e:
        print(e)
    finally:
        exit(0)


def test_mongodb():
    # set log name before importing... the import creates the log whatever it's file name
    debug.file_name = 'test_mongodb.log'
    log = debug.create_log()
    log.setLevel(20)
    from kairos import tools
    config = tools.get_config()
    log.setLevel(config.getint('logging', 'level'))

    connection_string = config.get('mongodb', 'connection_string')
    collection = config.get('mongodb', 'collection')

    from kairos import mongodb
    mongodb.test(connection_string, collection, log)
    exit(0)


def clean_browser_data():
    debug.file_name = 'clean_browser_data.log'
    log = debug.create_log()
    log.setLevel(20)
    from kairos import tools
    config = tools.get_config()
    log.setLevel(config.getint('logging', 'level'))

    DRIVER_TYPE = 'chromedriver'
    driver_count = sum(1 for process in psutil.process_iter() if process.name().startswith(DRIVER_TYPE))

    if config.has_option('webdriver', 'user_data_directory'):
        user_data_directory = config.get('webdriver', 'user_data_directory')
        user_data_base_dir, tail = os.path.split(user_data_directory)
        with os.scandir(user_data_base_dir) as user_data_directories:
            for entry in user_data_directories:
                # remove all directories that start with 'kairos_' followed by a number
                path = os.path.join(user_data_base_dir, entry)
                if (entry.name.startswith('kairos_') and not tools.path_in_use(path, log)) or (entry.name.startswith('kairos') and driver_count == 0):
                    if entry.name != user_data_directory:
                        try:
                            shutil.rmtree(path)
                            log.info("{} removed".format(entry.name))
                        except Exception as e:
                            log.exception(e)
                elif entry.name.startswith('kairos_'):
                    log.info("{} is in use and cannot be removed (close all instances of {} and try again)".format(entry.name, DRIVER_TYPE))
        log.info("cleaning complete")
    else:
        log.info("skipping. User data directory is not set in kairos.cfg")


def sort_back_test_data(filename, sort_by, reverse=True):
    from kairos import tools
    from tv import tv

    debug.file_name = 'sort_back_test_data.log'
    log = debug.create_log()
    log.setLevel(20)
    config = tools.get_config()
    log.setLevel(config.getint('logging', 'level'))
    # log.info("{} {} {}".format(filename, sort_by, reverse))

    path = os.path.join(os.path.curdir, filename)
    if os.path.exists(path):
        try:
            import json
            with open(path, 'r') as stream:
                data = json.load(stream)
                data = tv.back_test_sort(data, sort_by, reverse)
            with open(path, 'w') as stream:
                stream.write(json.dumps(data, indent=4))
        except Exception as e:
            log.exception(e)
    else:
        log.error("{} doesn't exist".format(filename))
        exit(1)


main()
