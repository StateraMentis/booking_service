from typing import TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseORM

if TYPE_CHECKING:
    from .booking import BookingORM
    from .timeslot import TimeSlotORM


class MeetingRoomORM(BaseORM):
    """
    Модель переговорной комнаты

    Attributes:
        name: Название переговорной комнаты (уникальное)
        description: Описание комнаты
        capacity: Вместимость комнаты (количество человек)
        is_active: Флаг активности комнаты
    """

    __tablename__ = "rooms"
    __table_args__ = {"comment": "Переговорные комнаты"}

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Название переговорной комнаты",
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Описание комнаты",
    )

    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
        comment="Вместимость комнаты (максимальное количество человек)",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Флаг доступности комнаты для бронирования",
    )

    # ===> RELATIONSHIPS <===
    time_slots: Mapped[list["TimeSlotORM"]] = relationship(
        "TimeSlotORM",
        back_populates="room",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="TimeSlotORM.start_time",
    )

    bookings: Mapped[list["BookingORM"]] = relationship(
        "BookingORM",
        back_populates="room",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="BookingORM.booking_date",
    )

    def __repr__(self) -> str:
        return f"<Room(id={self.id}, name='{self.name}', capacity={self.capacity})>"
