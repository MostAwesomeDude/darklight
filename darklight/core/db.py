#!/usr/bin/env python

import sqlalchemy

from darklight.core.file import DarkFile, DarkTTH

class DarkDB(object):

    handle = None

    def __init__(self, url):
        self.url = url
        self.engine = sqlalchemy.create_engine(self.url)

        self.initdb()

        self.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine)

    def initdb(self):
        DarkFile.metadata.create_all(self.engine)
        DarkTTH.metadata.create_all(self.engine)

    def update(self, f):
        if not self.sessionmaker:
            raise Exception("Not connected!")

        session = self.sessionmaker()

        query = session.query(DarkFile).filter_by(path=f.path)

        if query.count() == 0:
            f = DarkFile(f.path)
        else:
            f = query[0]

        session.add(f)
        session.commit()

    def verify(self, file):
        if not self.sessionmaker:
            raise Exception("Not connected!")

        session = self.sessionmaker()

        query = session.query(DarkFile).filter_by(path=file.path)

        if query.count() == 0:
            return

        f = query[0]

        if f.size != file.size or f.mtime != file.mtime:
            f.size = file.size
            f.mtime = file.mtime
            session.add(f)
            session.commit()
            file.dirty = True
        else:
            file.tth = f.tth
            file.dirty = False
