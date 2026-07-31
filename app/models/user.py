from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseORM
from app.enums import UserRole

if TYPE_CHECKING:
    from .booking import BookingORM


class UserORM(BaseORM):
    """
    Модель пользователя

    Attributes:
        username: Уникальное имя пользователя для входа
        email: Email пользователя
        password_hash: Хешированный пароль (bcrypt)
        full_name: Полное имя пользователя
        role: Роль пользователя в системе (employee/admin)
        is_active: Флаг активности аккаунта
        bookings: [relationship] Список бронирований, созданных пользователем
    """

    __tablename__ = "users"
    __table_args__ = {"comment": "Пользователи сервиса"}

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Уникальное имя пользователя для входа",
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email пользователя",
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Хешированный пароль (bcrypt)",
    )

    full_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Полное имя пользователя",
    )

    role: Mapped[UserRole] = mapped_column(
        SAEnum(
            UserRole,
            values_callable=lambda obj: [e.value for e in obj],
            name="booking_status_enum",
        ),
        nullable=False,
        default=UserRole.EMPLOYEE,
        comment="Роль пользователя в системе",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Флаг активности аккаунта",
    )

    # ===> RELATIONSHIPS <===
    bookings: Mapped[list["BookingORM"]] = relationship(
        "BookingORM",
        foreign_keys="BookingORM.user_id",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # updated_bookings: Mapped[list["BookingORM"]] = relationship(
    #     "BookingORM",
    #     foreign_keys="BookingORM.updated_by_id",
    #     back_populates="updated_by",
    #     lazy="selectin",
    # )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
