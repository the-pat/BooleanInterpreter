#!/usr/bin/python

"""
Name: Patrick Tone
Language: Python
Version: 3.5.2

To evaluate the expression:
    interpreter.py -i <inputfile>
"""

import sys
import getopt
import os.path
from code.interpreter import Interpreter as Interpreter
from code.exceptions import SyntaxException as SyntaxException

__help = "{0}\r\n{1}\r\n".format(
    "USAGE:\r\n\tinterpreter.py -i <inputfile>",
    "Options:\r\n\t{0}\r\n\t{1}".format(
        "-i, --ifile: input file path",
        "-h, --help: get help"
    )
)

def main(argv):
    # Read commands from the terminal
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile="])
    except getopt.GetoptError:
        print("interpreter.py -i <inputfile>")
        sys.exit(2)

    # Ensure the valid commands are given
    # Valid commands are:
    #   help (-h, --help)
    #   input file (-i, --ifile)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print(__help)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            isValidCommand = True
            try:
                # arg = path to the input file
                interpreter = Interpreter(arg)
                value = interpreter.eval()
                if value is not None:
                    print("Given expression evaluates to: ", value)
            except SyntaxException as e:
                print(e)

    if not isValidCommand:
        print("type: 'interpreter.py --help' for help")

if __name__ == "__main__":
    main(sys.argv[1:])
