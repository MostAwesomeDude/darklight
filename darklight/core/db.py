import sqlalchemy

from darklight.core.file import DarkFile, DarkTTH

class DarkDB(object):

    handle = None

    def __init__(self, url):
        self.url = url
        self.engine = sqlalchemy.create_engine(self.url)

        self.initdb()

        self.sessionmaker = sqlalchemy.orm.scoped_session(
            sqlalchemy.orm.sessionmaker(bind=self.engine))

    def initdb(self):
        DarkFile.metadata.create_all(self.engine)
        DarkTTH.metadata.create_all(self.engine)

    def get_or_create_file(self, path):
        """
        Retrieve a DarkFile for a path, optionally creating it if it does not
        already exist.

        Files will be hashed if necessary.
        """

        if not self.sessionmaker:
            raise Exception("Not connected!")

        session = self.sessionmaker()

        f = session.query(DarkFile).filter_by(path=path).first()

        if not f:
            f = DarkFile(path)
            session.add(f)

        f.clean()
        session.commit()
        return f

    def find_branch(self, hash, size):
        """
        Find a hash branch, or return None.
        """

        if not self.sessionmaker:
            raise Exception("Not connected!")

        session = self.sessionmaker()

        return session.query(DarkTTH).filter_by(hash=hash, size=size).first()

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
