#!/usr/bin/env python

import sqlalchemy

from darklight.core.file import DarkFile

class DarkDB(object):
    url = "sqlite:///darklight.db"
    handle = None

    def connect(self):
        self.engine = sqlalchemy.create_engine(self.url)

        self.initdb()

        self.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine)
        return True

    def initdb(self):
        DarkFile.metadata.create_all(self.engine)

    def update(self, file):
        if not self.sessionmaker:
            raise Exception, "Not connected!"

        session = self.sessionmaker()

        query = session.query(DarkFile).filter_by(path=file.path)

        if query.count() == 0:
            f = DarkFile(file.path)
        else:
            f = query[0]

        f.size = file.size
        f.mtime = file.mtime
        f.tth = file.tth
        session.add(f)
        session.commit()
        file.serial = f.serial

    def verify(self, file):
        if not self.sessionmaker:
            raise Exception, "Not connected!"

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
