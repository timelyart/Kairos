import sys
from tv import mail

TEST = True


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
    print("-h\t\t Flag. Show this help.")
    print("-d\t\t Flag. Show disclaimer.\n")


def main():
    from tv import tv

    try:
        print_disclaimer()
        print("USAGE:\npython main.py [<file>] [-s|-s <minutes>] [-h] [-d]")
        print("For help, type: python main.py -h\n\n")

        yaml = ""
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
            elif i > 1 and str(sys.argv[(i-1)]) == '-s':
                delay_summary = int(sys.argv[i])
            elif not str(sys.argv[i]).endswith('main.py'):
                print("No such argument: " + str(sys.argv[i]))
            i += 1

        triggered_signals = []
        if len(yaml) > 0:
            send_signals_immediately = not send_summary
            triggered_signals = tv.run(yaml, send_signals_immediately)
        if send_summary:
            mail.run(delay_summary, yaml, triggered_signals)
    except Exception as e:
        print(e)
    finally:
        exit(0)


main()
