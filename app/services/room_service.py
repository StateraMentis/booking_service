from datetime import date
from sqlalchemy.orm import Session

from app.repositories.room_repository import RoomRepository
from app.repositories.timeslot_repository import TimeSlotRepository
from app.repositories.booking_repository import BookingRepository
from app.api.schemas.room import RoomAvailabilityResponse, RoomCreate
from app.exceptions import (
    RoomNotFoundError,
    RoomAlreadyExistsError,
    RoomHasActiveBookingsError,
)
from app.models import MeetingRoomORM


class RoomService:
    """
    Сервис для управления переговорными комнатами
    """

    def __init__(
        self,
        db: Session,
        room_repo: RoomRepository,
        time_slot_repo: TimeSlotRepository,
        booking_repo: BookingRepository,
    ):
        self.db = db
        self.room_repo = room_repo
        self.time_slot_repo = time_slot_repo
        self.booking_repo = booking_repo

    def get_room_by_id(self, room_id: int) -> MeetingRoomORM | None:
        """
        Получить комнату по ID

        Args:
            room_id: ID комнаты

        Returns:
            MeetingRoomORM | None: Комната или None, если не найдена
        """

        return self.room_repo.get_by_id(room_id)

    def get_rooms(
        self,
        page: int = 1,
        size: int = 20,
        active_only: bool = True,
    ) -> tuple[list[MeetingRoomORM], int]:
        """
        Получить список комнат с пагинацией.

        Args:
            page: Номер страницы
            size: Количество записей на странице
            active_only: Фильтровать только активные комнаты

        Returns:
            tuple: (список комнат, общее количество)
        """

        skip = (page - 1) * size
        if active_only:
            return self.room_repo.get_active_rooms(skip=skip, limit=size)
        return self.room_repo.get_all(skip=skip, limit=size)

    def create_room(self, data: RoomCreate) -> MeetingRoomORM:
        """
        Создать новую комнату

        Args:
            data: Данные для создания комнаты

        Returns:
            MeetingRoomORM: Созданная комната

        Raises:
            RoomAlreadyExistsError: Комната с таким названием уже существует
        """

        if self.room_repo.get_by_name(data.name):
            raise RoomAlreadyExistsError("Комната с таким названием уже существует")

        return self.room_repo.create(**data.model_dump())

    def update_room(self, room_id: int, data: dict) -> MeetingRoomORM | None:
        """
        Обновить комнату.

        Args:
            room_id: ID комнаты
            data: Данные для обновления

        Returns:
            MeetingRoomORM | None: Обновленная комната или None, если не найдена

        Raises:
            RoomNotFoundError: Комната не найдена
            RoomAlreadyExistsError: Конфликт названия
        """

        room = self.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFoundError("Комната не найдена")

        if "name" in data:
            existing = self.room_repo.get_by_name(data["name"])
            if existing and existing.id != room_id:
                raise RoomAlreadyExistsError("Комната с таким названием уже существует")

        return self.room_repo.update(room_id, **data)

    def delete_room(self, room_id: int) -> bool:
        """
        Удалить комнату.

        Args:
            room_id: ID комнаты

        Returns:
            bool: True, если комната удалена, False в противном случае

        Raises:
            RoomNotFoundError: Комната не найдена
            RoomHasActiveBookingsError: Есть активные бронирования
        """

        room = self.room_repo.get_by_id(room_id)
        if not room:
            return False

        bookings = self.booking_repo.get_room_bookings(room_id)
        if bookings:
            raise RoomHasActiveBookingsError(
                "Невозможно удалить комнату с активными бронированиями"
            )

        return self.room_repo.delete(room_id)

    def check_availability(
        self,
        room_id: int,
        date: date,
    ) -> RoomAvailabilityResponse | None:
        """
        Проверить доступность комнаты на дату.

        Args:
            room_id: ID комнаты
            date: Дата для проверки

        Returns:
            RoomAvailabilityResponse | None: Данные о доступности
        """

        room = self.room_repo.get_by_id(room_id)
        if not room:
            return None

        all_slots = self.time_slot_repo.get_active_slots_by_room(room_id)

        bookings = self.booking_repo.get_room_bookings(room_id, date)
        booked_slot_ids = {b.time_slot_id for b in bookings}

        available_slots = [s for s in all_slots if s.id not in booked_slot_ids]

        return {
            "room_id": room_id,
            "room_name": room.name,
            "capacity": room.capacity,
            "date": date.isoformat(),
            "available_slots": available_slots,
            "total_slots": len(all_slots),
            "booked_slots": len(booked_slot_ids),
            "is_fully_booked": len(available_slots) == 0,
        }
