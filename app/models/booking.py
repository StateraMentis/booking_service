from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Date, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseORM

if TYPE_CHECKING:
    from .room import MeetingRoomORM
    from .user import UserORM
    from .timeslot import TimeSlotORM


class BookingORM(BaseORM):
    """
    Модель бронирования переговорной комнаты.

    Attributes:
        room_id: ID комнаты (внешний ключ)
        time_slot_id: ID временного слота (внешний ключ)
        user_id: ID пользователя, создавшего бронирование (внешний ключ)
        booking_date: Дата бронирования
        description: Описание встречи/бронирования
        status: Статус бронирования (active/cancelled)
        cancelled_at: Дата и время отмены бронирования
        cancelled_by_id: ID пользователя, отменившего бронирование (внешний ключ)
        room: [relationship] Связь с моделью MeetingRoomORM
        time_slot: [relationship] Связь с моделью TimeSlotORM
        user: [relationship] Связь с моделью UserORM (создатель бронирования)
        cancelled_by: [relationship] Связь с моделью UserORM (отменивший бронирование)
    """

    __tablename__ = "bookings"
    __table_args__ = {"comment": "Переговорные комнаты"}

    room_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID комнаты",
    )

    time_slot_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("time_slots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID временного слота",
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID пользователя, создавшего бронирование",
    )

    booking_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Дата бронирования",
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Описание встречи/бронирования",
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="active",
        comment="Статус бронирования",
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата и время отмены бронирования",
    )

    cancelled_by_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID пользователя, отменившего бронирование",
    )

    # ===> RELATIONSHIPS <===
    room: Mapped["MeetingRoomORM"] = relationship(
        "MeetingRoomORM",
        back_populates="bookings",
        lazy="selectin",
        foreign_keys=[room_id],
    )

    time_slot: Mapped["TimeSlotORM"] = relationship(
        "TimeSlotORM",
        back_populates="bookings",
        lazy="selectin",
    )

    user: Mapped["UserORM"] = relationship(
        "UserORM",
        back_populates="bookings",
        lazy="selectin",
        foreign_keys=[user_id],
    )

    cancelled_by: Mapped[Optional["UserORM"]] = relationship(
        "UserORM",
        foreign_keys=[cancelled_by_id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Booking(id={self.id}, room_id={self.room_id}, "
            f"user_id={self.user_id}, date={self.booking_date}, "
            f"time_slot_id={self.time_slot_id}, "
            f"status='{self.status}')>"
        )
