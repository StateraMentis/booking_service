from sqlalchemy.orm import Session
from fastapi import Depends

from app.api.dependencies.database import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.timeslot_repository import TimeSlotRepository
from app.repositories.booking_repository import BookingRepository


def get_user_repository(
    db: Session = Depends(get_db),
) -> UserRepository:
    """
    Фабрика для создания репозитория пользователей

    Args:
        db: Сессия БД

    Returns:
        UserRepository: Репозиторий пользователей
    """

    return UserRepository(db)


def get_room_repository(
    db: Session = Depends(get_db),
) -> RoomRepository:
    """
    Фабрика для создания репозитория комнат

    Args:
        db: Сессия БД

    Returns:
        RoomRepository: Репозиторий комнат
    """

    return RoomRepository(db)


def get_time_slot_repository(
    db: Session = Depends(get_db),
) -> TimeSlotRepository:
    """
    Фабрика для создания репозитория временных слотов

    Args:
        db: Сессия БД

    Returns:
        TimeSlotRepository: Репозиторий слотов
    """

    return TimeSlotRepository(db)


def get_booking_repository(
    db: Session = Depends(get_db),
) -> BookingRepository:
    """
    Фабрика для создания репозитория бронирований

    Args:
        db: Сессия БД

    Returns:
        BookingRepository: Репозиторий бронирований
    """

    return BookingRepository(db)
