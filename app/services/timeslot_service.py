from sqlalchemy.orm import Session

from app.repositories.timeslot_repository import TimeSlotRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.booking_repository import BookingRepository
from app.exceptions import (
    TimeSlotNotFoundError,
    RoomNotFoundError,
)
from app.models import TimeSlotORM
from app.api.schemas import TimeSlotCreate


class TimeSlotService:
    """
    Сервис для управления временными слотами
    """

    def __init__(
        self,
        db: Session,
        time_slot_repo: TimeSlotRepository,
        room_repo: RoomRepository,
        booking_repo: BookingRepository,
    ):
        self.db = db
        self.time_slot_repo = time_slot_repo
        self.room_repo = room_repo
        self.booking_repo = booking_repo

    def get_room_slots(
        self, room_id: int, include_inactive: bool = False
    ) -> list[TimeSlotORM]:
        """
        Получить все слоты комнаты

        Args:
            room_id: ID комнаты
            include_inactive: Включать ли неактивные слоты

        Returns:
            list: Список слотов

        Raises:
            RoomNotFoundError: Комната не найдена
        """

        room = self.room_repo.get_by_id(room_id)
        if not room:
            raise RoomNotFoundError(f"Комната с ID {room_id} не найдена")

        return self.time_slot_repo.get_by_room(room_id, include_inactive)

    def create_time_slot(self, data: TimeSlotCreate) -> TimeSlotORM:
        """
        Создать новый временной слот

        Args:
            data: Данные для создания слота

        Returns:
            TimeSlotORM: Созданный слот

        Raises:
            RoomNotFoundError: Комната не найдена
            TimeSlotOverlapError: Слот пересекается с существующим
        """

        room = self.room_repo.get_by_id(data.room_id)
        if not room:
            raise RoomNotFoundError(f"Комната с ID {data.room_id} не найдена")

        self.time_slot_repo.ensure_no_overlap(
            room_id=data.room_id,
            start_time=data.start_time,
            end_time=data.end_time,
            day_of_week=data.day_of_week,
        )

        return self.time_slot_repo.create(**data.model_dump())

    def update_time_slot(self, slot_id: int, data: dict) -> TimeSlotORM | None:
        """
        Обновить временной слот

        Args:
            slot_id: ID слота
            data: Данные для обновления

        Returns:
            TimeSlotORM | None: Обновленный слот или None, если не найден

        Raises:
            TimeSlotNotFoundError: Слот не найден
            TimeSlotOverlapError: Слот пересекается с существующим
        """

        slot = self.time_slot_repo.get_by_id(slot_id)
        if not slot:
            raise TimeSlotNotFoundError("Временной слот не найден")

        if "start_time" in data or "end_time" in data:
            start_time = data.get("start_time", slot.start_time)
            end_time = data.get("end_time", slot.end_time)
            day_of_week = data.get("day_of_week", slot.day_of_week)

            self.time_slot_repo.ensure_no_overlap(
                room_id=slot.room_id,
                start_time=start_time,
                end_time=end_time,
                day_of_week=day_of_week,
                exclude_id=slot_id,
            )

        return self.time_slot_repo.update(slot_id, **data)

    def delete_time_slot(self, slot_id: int) -> bool:
        """
        Удалить временной слот

        Args:
            slot_id: ID слота

        Returns:
            bool: True, если слот удален, False в противном случае

        Raises:
            TimeSlotNotFoundError: Слот не найден
            TimeSlotHasActiveBookingsError: Есть активные бронирования
        """

        slot = self.time_slot_repo.get_by_id(slot_id)
        if not slot:
            return False

        return self.time_slot_repo.delete(slot_id)
