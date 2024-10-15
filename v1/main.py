import unittest
from contextlib import contextmanager
from typing import Iterator

import sqlalchemy
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
        self.engine: Engine = engine
        delete_targets_script = "drop table if exists funtion_storage;"
        delete_value_storage_script = "drop table if exists `value_storage`"
        value_storage_script = \
"""create table `value_storage`
(
    id char(36) not null primary key,
    data longtext collate utf8mb4_bin not null check (json_valid(`data`))
);"""
        targets_script = \
"""create table funtion_storage
(
	from_value_id char(36) not null,
	to_value_id char(36) not null,
	counter int default 0 not null,
	primary key (from_value_id, to_value_id),
	constraint fk_funtion_storage_from_value_id
		foreign key (from_value_id) references `value_storage` (id)
			on delete cascade,
	constraint fk_funtion_storage_to_value_id
		foreign key (to_value_id) references `value_storage` (id)
			on delete cascade
);
"""
        trigger_script = \
"""create definer = root@`%` trigger tr_funtion_storage_counter
	before insert
	on funtion_storage
	for each row
	BEGIN
        DECLARE existing_count INT;

        -- Check if the record with the same from_value_id, from_path and to_path exists
        SELECT COUNT(*)
        INTO existing_count
        FROM funtion_storage
        WHERE from_value_id = NEW.from_value_id
          AND to_value_id <> NEW.to_value_id;

        -- If there are existing records, update the counter field
        IF existing_count > 0 THEN
            SET NEW.counter = existing_count;
        END IF;
    END;
"""
        with open_session(self.engine) as session:
            session.execute(sqlalchemy.text(delete_targets_script))
            session.commit()
            session.execute(sqlalchemy.text(delete_value_storage_script))
            session.commit()
            session.execute(sqlalchemy.text(value_storage_script))
            session.commit()
            session.execute(sqlalchemy.text(targets_script))
            session.commit()
            session.execute(sqlalchemy.text(trigger_script))
            session.commit()

    def setUp(self):
        with open_session(self.engine) as session:
            for name in TableNames:
                session.execute(text(f"delete from {name}"))
                session.commit()

    @staticmethod
    def _db_value_storage() -> list[DBValue]:
        return [
            DBValue(
                id="1",
                data={},
                func_targets_from_me=[
                    FunctionTargets(
                        from_value_id="1",
                        to_value_id="2",
                    ),
                ]
            ),
            DBValue(
                id="2",
                data={},
                func_targets_from_me=[
                    FunctionTargets(
                        from_value_id="2",
                        to_value_id="1",
                    )
                ],
            ),
            DBValue(
                id="3",
                data={},
                func_targets_from_me=[
                    FunctionTargets(
                        from_value_id="3",
                        to_value_id="1",
                    )
                ],
            )
        ]

    def test1(self):
        with open_session(self.engine) as session:
            db_value_storage = self._db_value_storage()
            session.add_all(db_value_storage)
            session.commit()

        with open_session(self.engine) as session:
            db_value_storage: list[DBValue] = session.query(DBValue).all()
            db_value_storage_dict = {
                db_value.id: db_value
                for db_value in db_value_storage
            }
            db_value_storage_dict["1"].func_targets_from_me = [
                FunctionTargets(
                    from_value_id="1",
                    to_value_id="3",
                )
            ]
            session.commit()


if __name__ == "__main__":
    unittest.main()
