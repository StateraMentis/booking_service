from datetime import date
from sqlalchemy.orm import Session

from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.timeslot_repository import TimeSlotRepository
from app.repositories.user_repository import UserRepository
from app.api.schemas.booking import BookingCreate, BookingHistoryResponse
from app.models.booking import BookingORM
from app.exceptions import (
    BookingNotFoundError,
    BookingAlreadyCancelledError,
    SlotAlreadyBookedError,
    BookingPermissionError,
    RoomNotFoundError,
    TimeSlotNotFoundError,
    BookingDateInPastError,
    ValidationError,
)
from app.enums import BookingStatus


class BookingService:
    """
    Сервис для управления бронированиями
    """

    def __init__(
        self,
        db: Session,
        booking_repo: BookingRepository,
        room_repo: RoomRepository,
        time_slot_repo: TimeSlotRepository,
        user_repo: UserRepository,
    ):
        self.db = db
        self.booking_repo = booking_repo
        self.room_repo = room_repo
        self.time_slot_repo = time_slot_repo
        self.user_repo = user_repo

    def create_booking(self, data: BookingCreate, user_id: int) -> BookingORM:
        """
        Создать новое бронирование

        Args:
            data: Данные для создания бронирования
            user_id: ID пользователя

        Raises:
            RoomNotFoundError: Комната не найдена
            TimeSlotNotFoundError: Слот не найден
            BookingDateInPastError: Дата в прошлом
            SlotAlreadyBookedError: Слот уже занят
        """

        room = self.room_repo.get_by_id(data.room_id)
        if not room:
            raise RoomNotFoundError("Комната не найдена")

        time_slot = self.time_slot_repo.get_by_id(data.time_slot_id)
        if not time_slot:
            raise TimeSlotNotFoundError("Временной слот не найден")

        if time_slot.room_id != data.room_id:
            raise ValidationError("Слот не принадлежит указанной комнате")

        if data.booking_date < date.today():
            raise BookingDateInPastError("Нельзя бронировать на прошедшую дату")

        if not self.booking_repo.check_slot_availability(
            room_id=data.room_id,
            time_slot_id=data.time_slot_id,
            date=data.booking_date,
        ):
            raise SlotAlreadyBookedError("Слот уже забронирован на эту дату")

        booking_data = data.model_dump()
        booking_data["user_id"] = user_id
        booking_data["status"] = BookingStatus.ACTIVE.value

        return self.booking_repo.create(**booking_data)

    def get_booking_by_id(self, booking_id: int) -> BookingORM | None:
        """
        Получить бронирование по ID

        Args:
            booking_id: ID бронирования

        Returns:
            BookingORM | None: Бронирование или None, если не найдено
        """

        return self.booking_repo.get_by_id_with_relations(booking_id)

    def get_user_bookings(
        self,
        user_id: int,
        page: int = 1,
        size: int = 20,
        status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[BookingORM], int]:
        """
        Получить бронирования пользователя.

        Args:
            user_id: ID пользователя
            page: Номер страницы
            size: Количество записей на странице
            status: Фильтр по статусу
            date_from: Фильтр по дате начала
            date_to: Фильтр по дате конца

        Returns:
            tuple: (список бронирований, общее количество)
        """

        skip = (page - 1) * size
        return self.booking_repo.get_user_bookings(
            user_id,
            skip,
            size,
            status,
            date_from,
            date_to,
        )

    def get_user_booking_history(
        self, user_id: int, limit: int = 50
    ) -> BookingHistoryResponse:
        """
        Получить историю бронирований пользователя

        Args:
            user_id: ID пользователя
            limit: Максимальное количество записей в истории

        Returns:
            BookingHistoryResponse: История бронирований
        """

        bookings, total = self.booking_repo.get_user_bookings(
            user_id,
            skip=0,
            limit=limit,
        )

        active_count = sum(
            1 for b in bookings if b.status == BookingStatus.ACTIVE.value
        )
        cancelled_count = sum(
            1 for b in bookings if b.status == BookingStatus.CANCELLED.value
        )

        return {
            "total_bookings": total,
            "active_bookings": active_count,
            "cancelled_bookings": cancelled_count,
            "bookings": bookings,
        }

    def update_booking(
        self,
        booking_id: int,
        data: dict,
        user_id: int,
        is_admin: bool = False,
    ) -> BookingORM | None:
        """
        Обновить бронирование.

        Args:
            booking_id: ID бронирования
            data: Данные для обновления
            user_id: ID пользователя
            is_admin: Является ли пользователь администратором

        Returns:
            BookingORM | None: Обновленное бронирование или None, если не найден

        Raises:
            BookingNotFoundError: Бронирование не найдено
            BookingPermissionError: Нет прав
            BookingDateInPastError: Дата в прошлом
            SlotAlreadyBookedError: Слот уже занят
        """

        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError("Бронирование не найдено")

        if booking.user_id != user_id and not is_admin:
            raise BookingPermissionError(
                "У вас нет прав на изменение этого бронирования"
            )

        if booking.status == BookingStatus.CANCELLED.value:
            raise BookingAlreadyCancelledError(
                "Нельзя изменить отмененное бронирование"
            )

        if "date" in data and data["date"] < date.today():
            raise BookingDateInPastError("Нельзя бронировать на прошедшую дату")

        if "time_slot_id" in data or "date" in data:
            new_time_slot_id = data.get("time_slot_id", booking.time_slot_id)
            new_date = data.get("date", booking.booking_date)

            if not self.booking_repo.check_slot_availability(
                room_id=booking.room_id,
                time_slot_id=new_time_slot_id,
                date=new_date,
                exclude_id=booking_id,
            ):
                raise SlotAlreadyBookedError("Выбранный слот уже занят")

        return self.booking_repo.update(booking_id, **data)

    def cancel_booking(
        self,
        booking_id: int,
        user_id: int,
        is_admin: bool = False,
    ) -> BookingORM | None:
        """
        Отменить бронирование

        Args:
            booking_id: ID бронирования
            user_id: ID пользователя
            is_admin: Является ли пользователь администратором

        Returns:
            BookingORM | None: Отмененное бронирование или None, если не найдено

        Raises:
            BookingNotFoundError: Бронирование не найдено
            BookingPermissionError: Нет прав
            BookingAlreadyCancelledError: Бронирование уже отменено
        """

        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise BookingNotFoundError("Бронирование не найдено")

        if booking.user_id != user_id and not is_admin:
            raise BookingPermissionError("У вас нет прав на отмену этого бронирования")

        if booking.status == BookingStatus.CANCELLED.value:
            raise BookingAlreadyCancelledError("Бронирование уже отменено")

        return self.booking_repo.cancel_booking(booking_id, user_id)

    def get_all_bookings(
        self,
        page: int = 1,
        size: int = 20,
        user_id: int | None = None,
        room_id: int | None = None,
        status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[BookingORM], int]:
        """
        Получить все бронирования с фильтрами (для администратора)

        Args:
            page: Номер страницы
            size: Количество записей на странице
            user_id: Фильтр по ID пользователя
            room_id: Фильтр по ID комнаты
            status: Фильтр по статусу бронирования
            date_from: Фильтр по дате начала диапазона
            date_to: Фильтр по дате конца диапазона

        Returns:
            tuple: (список бронирований, общее количество)
        """
        skip = (page - 1) * size
        return self.booking_repo.get_all_bookings(
            skip,
            size,
            user_id,
            room_id,
            status,
            date_from,
            date_to,
        )
