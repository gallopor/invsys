from sqlalchemy.orm import sessionmaker, scoped_session
from orm import DB_ENGINE

from contextlib import contextmanager

# 相比直接用sessionmaker，scoped_session返回的对象构造出来的对话对象是全局唯一的，不同的对话对象实例都指向一个对象引用
SessionType = scoped_session(sessionmaker(bind=DB_ENGINE))


def get_session():
    return SessionType()


@contextmanager
def connect_scope():
    conn = DB_ENGINE.connect()
    trans = conn.begin()
    try:
        yield trans
        trans.commit()
    except:
        trans.rollback()
    finally:
        conn.close()


@contextmanager
def session_scope():
    session = get_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def table_cleanup(self, table):
    self.engine.execute(table.delete())
