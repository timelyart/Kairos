# noinspection PyUnresolvedReferences
from kairos import timing
from tv import tv


def print_disclaimer():
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


def main():
    try:
        print_disclaimer()
        tv.run()
    finally:
        exit(0)


main()
