#!/usr/bin/env python

import pickle

import sqlalchemy
import sqlalchemy.ext.declarative

class File(sqlalchemy.ext.declarative.declarative_base()):

    __tablename__ = "files"

    serial = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    path = sqlalchemy.Column(sqlalchemy.String)
    size = sqlalchemy.Column(sqlalchemy.Integer)
    mtime = sqlalchemy.Column(sqlalchemy.Integer)
    tth = sqlalchemy.Column(sqlalchemy.LargeBinary)

class DarkDB:
    url = "sqlite:///darklight.db"
    handle = None

    def connect(self):
        self.engine = sqlalchemy.create_engine(self.url)

        self.initdb()

        self.sessionmaker = sqlalchemy.orm.sessionmaker(bind=self.engine)
        return True

    def initdb(self):
        File.metadata.create_all(self.engine)

    def update(self, file):
        if not self.sessionmaker:
            raise Exception, "Not connected!"

        session = self.sessionmaker()

        buf = buffer(pickle.dumps(file.tth, 1))
        query = session.query(File).filter_by(path=file.path)

        if query.count() == 0:
            f = File()
            f.path = file.path
        else:
            f = query[0]

        f.size = file.size
        f.mtime = file.mtime
        f.tth = buf
        session.add(f)
        session.commit()
        file.serial = f.serial

    def verify(self, file):
        if not self.sessionmaker:
            raise Exception, "Not connected!"

        session = self.sessionmaker()

        query = session.query(File).filter_by(path=file.path)

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
            file.tth = pickle.loads(f.tth)
            file.dirty = False
