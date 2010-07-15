#!/usr/bin/env python

import os
import pickle
import sys

try:
    import apsw
except ImportError:
    print "Fatal error: Couldn't find APSW module..."
    sys.exit()

class DarkDB:
    path = "darklight.db"
    handle = None

    def connect(self):
        if not os.path.exists(self.path):
            self.initdb()
        if not self.handle:
            self.handle = apsw.Connection(self.path)
        return True

    def initdb(self):
        self.handle = apsw.Connection(self.path)
        cursor = handle.cursor()
        cursor.execute("create table files(serial primary key, path text, size, mtime, tth blob)")

    def update(self, file):
        if not self.handle:
            raise Exception, "Not connected!"

        cursor = self.handle.cursor()
        cursor.execute("select * from files where path=?", (file.path,))
        temp = [i for i in cursor]
        buf = buffer(pickle.dumps(file.tth, 1))
        if len(temp) == 0:
            cursor.execute("insert into files values (null,?,?,?,?)", (file.path, file.size, file.mtime, buf))
            file.serial = self.handle.last_insert_rowid()
        else:
            cursor.execute("update files set size=?, mtime=?, tth=? where path=?", (file.size, file.mtime, buf, file.path))

    def verify(self, file):
        if not self.handle:
            raise Exception, "Not connected!"

        cursor = self.handle.cursor()
        cursor.execute("select * from files where path=?", (file.path,))
        try:
            serial, path, size, mtime, hashblob = next(cursor)
        except StopIteration:
            return
        if size != file.size or mtime != file.mtime:
            cursor.execute("update files set size=?, mtime=? where path=?",
                (file.size, file.mtime, file.path))
            file.dirty = True
        else:
            file.tth = pickle.loads(hashblob)
            file.dirty = False
