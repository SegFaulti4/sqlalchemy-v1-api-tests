import enum
from typing import Optional

from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped, Session
from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm.collections import attribute_keyed_dict


class Base(DeclarativeBase):
    pass


class Tables(str, enum.Enum):
    FUNCTIONS = "function_storage"
    VALUES = "value_storage"
    NODES = "node_storage"


class Functions(Base):
    __tablename__ = Tables.FUNCTIONS.value

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)
    value_id: Mapped[int] = mapped_column(
        ForeignKey(
            f"{Tables.VALUES.value}.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )


class Values(Base):
    __tablename__ = Tables.VALUES.value

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)
    node_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            f"{Tables.NODES.value}.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
    )
    functions: Mapped[dict[int, Functions]] = relationship(
        Functions.__name__,
        foreign_keys="[Functions.value_id]",
        collection_class=attribute_keyed_dict("id"),
        cascade="all, delete, delete-orphan, merge",
        passive_deletes=True,
        passive_updates=True,
    )


class Nodes(Base):
    __tablename__ = Tables.NODES.value

    id: Mapped[int] = mapped_column(primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)
    values: Mapped[dict[int, Values]] = relationship(
        Values.__name__,
        foreign_keys="[Values.node_id]",
        collection_class=attribute_keyed_dict("id"),
        cascade="all, delete, delete-orphan, merge",
        passive_deletes=True,
        passive_updates=True,
    )
