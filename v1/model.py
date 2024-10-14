import enum

from sqlalchemy import Column, INT, ForeignKey
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Tables(enum.StrEnum):
    FUNCTIONS = "function_storage"
    VALUES = "value_storage"


class DBFunction(Base):
    __tablename__ = str(Tables.FUNCTIONS)
    id = Column(INT, primary_key=True, nullable=False)
    counter = Column(INT, nullable=False)
    data = Column(JSON, nullable=False)
    value_id = Column(INT, ForeignKey("value_storage.id"), nullable=False)


class DBValue(Base):
    __tablename__ = str(Tables.VALUES)

    id = Column(INT, primary_key=True, nullable=False)
    data = Column(JSON, nullable=False)

    functions: list[DBFunction] = relationship(
        DBFunction.__name__,
        cascade="all, delete-orphan",
        foreign_keys="[DBFunction.value_id]",
    )
