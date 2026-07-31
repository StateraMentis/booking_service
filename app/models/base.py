from datetime import datetime
from sqlalchemy import Integer, DateTime, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class BaseORM(DeclarativeBase):
    """
    Абстрактная базовая модель для всех таблиц

    Attributes:
        id: ID записи в таблице
        added_at: Дата/время добавления записи в таблицу
        updated_at: Дата/время последнего обновления записи
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        comment="ID записи (автоинкремент)",
    )

    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Дата/время добавления записи в таблицу",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Дата/время последнего обновления записи",
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
