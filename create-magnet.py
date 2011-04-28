#!/usr/bin/env python

import sys

from darklight.core.db import DarkDB
from darklight.core.file import DarkFile
from darklight.magnet import create_magnet

db = DarkDB("sqlite:///darklight.db")

name = sys.argv[-1]

dfile = db.sessionmaker().query(DarkFile).filter_by(path=name).first()

if not dfile:
    sys.exit(-1)

dfile.clean()

print create_magnet(dfile.tth.size, dfile.tth.hash)
