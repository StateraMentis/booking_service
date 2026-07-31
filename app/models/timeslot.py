from typing import TYPE_CHECKING
from sqlalchemy import Time, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseORM

if TYPE_CHECKING:
    from .room import MeetingRoomORM
    from .booking import BookingORM


class TimeSlotORM(BaseORM):
    """
    Модель временного слота комнаты

    Attributes:
        room_id: ID комнаты (внешний ключ)
        start_time: Время начала слота
        end_time: Время окончания слота
        is_active: Флаг активности слота
        day_of_week: День недели (0=понедельник), если слот повторяется не каждый день
        room: [relationship] Связь с моделью MeetingRoomORM
        bookings: [relationship] Список бронирований, связанных с этим слотом
    """

    __tablename__ = "time_slots"

    room_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID комнаты",
    )

    start_time: Mapped[str] = mapped_column(
        Time,
        nullable=False,
        comment="Время начала слота",
    )

    end_time: Mapped[str] = mapped_column(
        Time,
        nullable=False,
        comment="Время окончания слота",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Флаг доступности слота для бронирования",
    )

    day_of_week: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="День недели (0=понедельник), если слот повторяется не каждый день",
    )

    # ===> RELATIONSHIPS <===
    room: Mapped["MeetingRoomORM"] = relationship(
        "MeetingRoomORM",
        back_populates="time_slots",
        lazy="selectin",
    )

    bookings: Mapped[list["BookingORM"]] = relationship(
        "BookingORM",
        back_populates="time_slot",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "start_time",
            "end_time",
            name="uq_room_time_slot",
        ),
        {"comment": "Временные слоты переговорных комнат"},
    )

    def __repr__(self) -> str:
        return f"<TimeSlot(id={self.id}, room_id={self.room_id}, {self.start_time}-{self.end_time})>"
