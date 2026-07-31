from enum import Enum


class UserRole(str, Enum):
    """
    Роли пользователей в системе
    """

    EMPLOYEE = "employee"
    ADMIN = "admin"


class BookingStatus(str, Enum):
    """
    Статус бронирования
    """

    ACTIVE = "active"
    CANCELLED = "cancelled"
