import unittest
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool

from orm import Functions, Values, Nodes, Base, Tables


class ORMTests(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        url = URL.create(
            "mysql+pymysql",
            username="root",
            password="example",
            host="localhost",
            database="storage",
            port=3306,
        )
        engine: Engine = create_engine(url, poolclass=NullPool)
        engine.connect()
        Base.metadata.create_all(engine)
        self.engine: Engine = engine

    def setUp(self) -> None:
        with Session(self.engine) as session:
            for name in Tables:
                session.execute(text(f"delete from {name}"))
                session.commit()

    @classmethod
    def _value_1(cls) -> Values:
        return Values(
            id=1, data={}, node_id=None,
            functions={
                1: Functions(id=1, data={}, value_id=1),
            },
        )

    @classmethod
    def _node_1(cls) -> Nodes:
        return Nodes(
            id=1, data={},
            values={
                Values(
                    id=2, data={}, node_id=1,
                    functions={

                    }
                )
            },
        )

    @classmethod
    def _get_obj_by_id(cls, session: Session, table: Any, obj_id: int) -> Any:
        return session.query(table).filter_by(id=obj_id).one()

    def test_merge_relationship_unset(self) -> None:
        """
        If we `session.merge` objects with unset relationships
        related objects will not be deleted
        """
        with Session(self.engine) as session:
            # add Value the usual way
            db_value = self._value_1()
            session.add(db_value)
            session.commit()

        with Session(self.engine) as session:
            # merge Value with unset relationship
            db_value = Values(id=1, data={}, node_id=None)
            session.merge(db_value)
            session.commit()

        with Session(self.engine) as session:
            db_value = self._get_obj_by_id(session, Values, 1)
            # the relationship should not be changed
            assert len(db_value.functions) == len(self._value_1().functions)

    def test_merge_relationship_unset_cascade(self) -> None:
        with Session(self.engine) as session:
            # add Value the usual way
            db_value = self._value_1()
            session.add(db_value)
            session.commit()

        with Session(self.engine) as session:
            # add Value with unset relationship
            db_value = Values(id=1, data={}, node_id=None)
            session.add(db_value)
            session.commit()

        with Session(self.engine) as session:
            db_value = self._get_obj_by_id(session, Values, 1)
            # the relationship should not be changed
            assert len(db_value.functions) == 1


def add_node(session: Session) -> None:
    node = Nodes(
        id=1,
        data={},
        values={
            1: Values(id=1, data={}, node_id=1, functions={}),
            2: Values(
                id=2,
                data={},
                node_id=1,
                functions={
                    1: Functions(id=1, data={}, value_id=2),
                },
            ),
            3: Values(
                id=3,
                data={},
                node_id=1,
                functions={
                    2: Functions(id=2, data={}, value_id=3),
                },
            ),
        },
    )


if __name__ == "__main__":
    unittest.main()
