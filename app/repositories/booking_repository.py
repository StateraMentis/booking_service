from datetime import date, datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func

from app.repositories.base import BaseRepository
from app.models.booking import BookingORM
from app.enums import BookingStatus


class BookingRepository(BaseRepository[BookingORM]):
    """
    Репозиторий для работы с бронированиями
    """

    def __init__(self, db: Session):
        super().__init__(BookingORM, db)

    def get_by_id_with_relations(self, booking_id: int) -> BookingORM | None:
        """
        Получить бронирование со всеми связями

        Args:
            booking_id: ID бронирования

        Returns:
            BookingORM | None: Бронирование или None, если не найдено
        """

        return (
            self.db.execute(
                select(BookingORM)
                .options(
                    joinedload(BookingORM.room),
                    joinedload(BookingORM.time_slot),
                    joinedload(BookingORM.user),
                    joinedload(BookingORM.cancelled_by),
                )
                .where(BookingORM.id == booking_id)
            )
            .unique()
            .scalar_one_or_none()
        )

    def get_user_bookings(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[BookingORM], int]:
        """
        Получить бронирования пользователя с фильтрами

        Args:
            user_id: ID пользователя
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            status: Фильтр по статусу
            date_from: Дата начала диапазона
            date_to: Дата конца диапазона

        Returns:
            tuple: (список бронирований, общее количество)
        """

        query = select(BookingORM).where(BookingORM.user_id == user_id)

        if status:
            query = query.where(BookingORM.status == status)

        if date_from:
            query = query.where(BookingORM.booking_date >= date_from)

        if date_to:
            query = query.where(BookingORM.booking_date <= date_to)

        query = query.order_by(BookingORM.booking_date.desc(), BookingORM.time_slot_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0

        query = query.offset(skip).limit(limit)
        items = self.db.execute(query).scalars().all()

        return items, total

    def get_room_bookings(
        self,
        room_id: int,
        date: date | None = None,
        status: str = BookingStatus.ACTIVE.value,
    ) -> list[BookingORM]:
        """
        Получить бронирования комнаты

        Args:
            room_id: ID комнаты
            date: Дата бронирования (опционально)
            status: Статус бронирования (по умолчанию ACTIVE)

        Returns:
            list: Список бронирований
        """

        query = select(BookingORM).where(
            BookingORM.room_id == room_id, BookingORM.status == status
        )

        if date:
            query = query.where(BookingORM.booking_date == date)

        query = query.order_by(BookingORM.booking_date, BookingORM.time_slot_id)
        return self.db.execute(query).scalars().all()

    def get_all_bookings(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: int | None = None,
        room_id: int | None = None,
        status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[BookingORM], int]:
        """
        Получить все бронирования с фильтрами (для администратора)

        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей в ответе
            user_id: Фильтр по ID пользователя
            room_id: Фильтр по ID комнаты
            status: Фильтр по статусу бронирования
            date_from: Фильтр по дате начала диапазона
            date_to: Фильтр по дате конца диапазона

        Returns:
            tuple: (список бронирований, общее количество)
        """

        query = select(BookingORM)

        if user_id:
            query = query.where(BookingORM.user_id == user_id)

        if room_id:
            query = query.where(BookingORM.room_id == room_id)

        if status:
            query = query.where(BookingORM.status == status)

        if date_from:
            query = query.where(BookingORM.booking_date >= date_from)

        if date_to:
            query = query.where(BookingORM.booking_date <= date_to)

        query = query.order_by(BookingORM.booking_date.desc())

        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0

        query = query.offset(skip).limit(limit)
        items = self.db.execute(query).scalars().all()

        return items, total

    def check_slot_availability(
        self,
        room_id: int,
        time_slot_id: int,
        date: date,
        exclude_id: int | None = None,
    ) -> bool:
        """
        Проверить доступность слота

        Args:
            room_id: ID комнаты
            time_slot_id: ID временного слота
            date: Дата бронирования
            exclude_id: ID бронирования, которое нужно исключить из проверки (например, при обновлении)

        Returns:
            bool: True если слот свободен
        """

        query = select(BookingORM).where(
            BookingORM.room_id == room_id,
            BookingORM.time_slot_id == time_slot_id,
            BookingORM.booking_date == date,
            BookingORM.status == BookingStatus.ACTIVE.value,
        )

        if exclude_id:
            query = query.where(BookingORM.id != exclude_id)

        return self.db.execute(query).first() is None

    def cancel_booking(
        self, booking_id: int, cancelled_by_id: int
    ) -> BookingORM | None:
        """
        Отменить бронирование

        Args:
            booking_id: ID бронирования
            cancelled_by_id: ID пользователя, который отменяет бронирование

        Returns:
            BookingORM | None: Отмененное бронирование или None, если не найдено или уже отменено
        """

        booking = self.get_by_id(booking_id)
        if not booking or booking.status == BookingStatus.CANCELLED.value:
            return None

        booking.status = BookingStatus.CANCELLED.value
        booking.cancelled_at = datetime.now()
        booking.cancelled_by_id = cancelled_by_id

        self.db.commit()
        self.db.refresh(booking)
        return booking
