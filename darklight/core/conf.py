#!/usr/bin/env python

import ConfigParser

class DarkConf(ConfigParser.SafeConfigParser):
    """An object that parses configuration."""

    def __init__(self):
        ConfigParser.SafeConfigParser.__init__(self)
        self.populate()

    def populate(self):
        """Load the default settings."""

        self.add_section("cache")
        self.set("cache", "size", str(10 * 1024 * 1024))
        self.set("cache", "hash-style", "lazy")

        self.add_section("database")
        self.set("database", "url", "sqlite:///darklight.db")

        self.add_section("folders")

        self.add_section("ssl")
        self.set("ssl", "enabled", str(False))
        self.set("ssl", "key", "")
        self.set("ssl", "certificate", "")

        self.add_section("passthrough")
        self.set("passthrough", "host", "localhost")
        self.set("passthrough", "port", str(80))
