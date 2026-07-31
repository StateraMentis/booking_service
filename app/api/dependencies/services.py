from sqlalchemy.orm import Session
from fastapi import Depends

from app.api.dependencies.database import get_db
from app.api.dependencies.repositories import (
    get_user_repository,
    get_room_repository,
    get_time_slot_repository,
    get_booking_repository,
)
from app.repositories.user_repository import UserRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.timeslot_repository import TimeSlotRepository
from app.repositories.booking_repository import BookingRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.room_service import RoomService
from app.services.timeslot_service import TimeSlotService
from app.services.booking_service import BookingService


def get_auth_service(
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """
    Фабрика для создания сервиса аутентификации

    Args:
        db: Сессия БД
        user_repo: Репозиторий пользователей

    Returns:
        AuthService: Сервис аутентификации
    """

    return AuthService(db, user_repo)


def get_user_service(
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    """
    Фабрика для создания сервиса пользователей

    Args:
        db: Сессия БД
        user_repo: Репозиторий пользователей

    Returns:
        UserService: Сервис пользователей
    """

    return UserService(db, user_repo)


def get_room_service(
    db: Session = Depends(get_db),
    room_repo: RoomRepository = Depends(get_room_repository),
    time_slot_repo: TimeSlotRepository = Depends(get_time_slot_repository),
    booking_repo: BookingRepository = Depends(get_booking_repository),
) -> RoomService:
    """
    Фабрика для создания сервиса комнат

    Args:
        db: Сессия БД
        room_repo: Репозиторий комнат
        time_slot_repo: Репозиторий слотов
        booking_repo: Репозиторий бронирований

    Returns:
        RoomService: Сервис комнат
    """

    return RoomService(db, room_repo, time_slot_repo, booking_repo)


def get_time_slot_service(
    db: Session = Depends(get_db),
    time_slot_repo: TimeSlotRepository = Depends(get_time_slot_repository),
    room_repo: RoomRepository = Depends(get_room_repository),
    booking_repo: BookingRepository = Depends(get_booking_repository),
) -> TimeSlotService:
    """
    Фабрика для создания сервиса временных слотов

    Args:
        db: Сессия БД
        time_slot_repo: Репозиторий слотов
        room_repo: Репозиторий комнат
        booking_repo: Репозиторий бронирований

    Returns:
        TimeSlotService: Сервис временных слотов
    """

    return TimeSlotService(db, time_slot_repo, room_repo, booking_repo)


def get_booking_service(
    db: Session = Depends(get_db),
    booking_repo: BookingRepository = Depends(get_booking_repository),
    room_repo: RoomRepository = Depends(get_room_repository),
    time_slot_repo: TimeSlotRepository = Depends(get_time_slot_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> BookingService:
    """
    Фабрика для создания сервиса бронирований

    Args:
        db: Сессия БД
        booking_repo: Репозиторий бронирований
        room_repo: Репозиторий комнат
        time_slot_repo: Репозиторий слотов
        user_repo: Репозиторий пользователей

    Returns:
        BookingService: Сервис бронирований
    """

    return BookingService(db, booking_repo, room_repo, time_slot_repo, user_repo)
