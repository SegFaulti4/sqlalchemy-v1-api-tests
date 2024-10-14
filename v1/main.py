import unittest
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session

from model import *
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.pool import NullPool


@contextmanager
def open_session(engine: Engine) -> Iterator[Session]:
    session = Session(engine, autoflush=False)
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


class Tests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        url = URL(
            "mysql+pymysql",
            username="root",
            password="example",
            host="localhost",
            database="storage",
            port=3306,
        )
        engine: Engine = create_engine(url, poolclass=NullPool, echo=True)
        engine.connect()
        Base.metadata.create_all(engine)
        self.engine: Engine = engine

    def setUp(self):
        with open_session(self.engine) as session:
            for name in Tables:
                session.execute(text(f"delete from {name}"))
                session.commit()

    @staticmethod
    def _value_1() -> DBValue:
        return DBValue(
            id=1,
            data={1: 1},
            functions=[
                DBFunction(
                    id=1,
                    value_id=1,
                    data={1: 1},
                    counter=1,
                )
            ],
        )

    def test1(self):
        with open_session(self.engine) as session:
            db_value = self._value_1()
            session.add(db_value)
            session.commit()

        with open_session(self.engine) as session:
            db_value = session.query(DBValue).filter(DBValue.id == 1).one()
            db_value.data = {1: 1}
            db_value.functions[0].counter = 2
            db_value.functions.append(
                DBFunction(
                    id=2,
                    value_id=1,
                    data={2: 2},
                    counter=2,
                )
            )
            session.commit()


if __name__ == "__main__":
    unittest.main()
