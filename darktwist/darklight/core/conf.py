#!/usr/bin/env python

import ConfigParser
import os

from cache import DarkCache
from db import DarkDB

import logging
logging.basicConfig(level=logging.DEBUG)

def populate(parser):
    """Load the default settings."""

    parser.add_section("cache")
    parser.set("cache", "size", str(10 * 1024 * 1024))
    parser.set("cache", "hash-style", "lazy")

    parser.add_section("database")
    parser.set("database", "path", "darklight.db")

    parser.add_section("folders")

    parser.add_section("ssl")
    parser.set("ssl", "enabled", str(False))
    parser.set("ssl", "key", "")
    parser.set("ssl", "certificate", "")

class DarkConf(object):
    """An object that parses configuration."""

    def __init__(self):
        self.parser = ConfigParser.SafeConfigParser()
        populate(self.parser)
