#!/usr/bin/env python

import readline
import sys

import twisted.internet.reactor

from darklight.client import DarkClientFactory

introduction = """
Welcome to the DarkLight client shell!
"""

def quit():
    print "Halting the reactor..."
    twisted.internet.reactor.stop()

commands = {"quit": quit}

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
