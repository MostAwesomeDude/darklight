#!/usr/bin/env python

import readline
import sys

import twisted.internet.reactor

from darklight.client import DarkClientFactory

introduction = """
Welcome to the DarkLight client shell!
"""

def help(*args):
    """
    Print a summary of all available commands, or get help on a specific
    command.

    Usage: help [command]
    """

    if args:
        for arg in args:
            if arg in commands:
                print "%s: %s" % (arg, commands[arg].__doc__)
            else:
                print "Unknown command %s" % arg
    else:
        for name, function in sorted(commands.iteritems()):
            print "%s: %s" % (name, function.__doc__)

def quit(*args):
    """
    Quit DL.
    """

    print "Halting the reactor..."
    twisted.internet.reactor.stop()

commands = {
    "exit": quit,
    "help": help,
    "quit": quit,
}

def mainloop():
    command = raw_input("dl> ")
    try:
        command, arguments = command.split(" ", 1)
        arguments = arguments.split(" ")
    except ValueError:
        arguments = tuple()

    if command in commands:
        commands[command](*arguments)

    twisted.internet.reactor.callLater(0, mainloop)

def main():

    print introduction

    twisted.internet.reactor.callWhenRunning(mainloop)
    twisted.internet.reactor.run()

    sys.exit()

if __name__ == "__main__":
    main()
