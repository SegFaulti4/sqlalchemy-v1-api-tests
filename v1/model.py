from __future__ import annotations

import enum
from typing import Annotated

from sqlalchemy import Column, INT, ForeignKey, CHAR
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, RelationshipProperty

Base = declarative_base()


class TableNames(enum.StrEnum):
    FUNCTION_TARGETS_TABLE = "funtion_storage"
    VALUES_TABLE = "value_storage"


id_str = Annotated[str, 36]
ID_STR = CHAR(36)
DICT = JSON


class FunctionTargets(Base):
    __tablename__ = TableNames.FUNCTION_TARGETS_TABLE

    from_value_id: Column[id_str] = Column(
        ID_STR,
        ForeignKey(
            f"{TableNames.VALUES_TABLE}.id",
            ondelete="CASCADE",
            onupdate="RESTRICT",
        ),
        primary_key=True,
        nullable=False,
    )
    to_value_id: Column[id_str] = Column(
        ID_STR,
        ForeignKey(
            f"{TableNames.VALUES_TABLE}.id",
            ondelete="CASCADE",
            onupdate="RESTRICT",
        ),
        primary_key=True,
        nullable=False,
    )
    counter: Column[int] = Column(INT, server_default="0", nullable=False)

    to_value: RelationshipProperty[DBValue] = relationship(
        "DBValue",
        foreign_keys="[FunctionTargets.to_value_id]",
        viewonly=True,
        uselist=False,
        cascade="",
        lazy="joined",
    )


class DBValue(Base):
    __tablename__ = TableNames.VALUES_TABLE

    id: Column[id_str] = Column(ID_STR, primary_key=True, nullable=False)
    data: Column[dict] = Column(DICT, nullable=False)

    func_targets_from_me: RelationshipProperty[list[FunctionTargets]] = relationship(  # type: ignore[misc]
        FunctionTargets.__name__,
        cascade="all, delete-orphan",
        passive_deletes=True,
        foreign_keys=[FunctionTargets.from_value_id],
        order_by=FunctionTargets.counter,
        lazy="selectin",
    )
