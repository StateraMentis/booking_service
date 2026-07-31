from datetime import time
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.repositories.base import BaseRepository
from app.models.timeslot import TimeSlotORM
from app.exceptions import TimeSlotOverlapError


class TimeSlotRepository(BaseRepository[TimeSlotORM]):
    """
    Репозиторий для работы с временными слотами
    """

    def __init__(self, db: Session):
        super().__init__(TimeSlotORM, db)

    def get_by_room(
        self, room_id: int, include_inactive: bool = False
    ) -> list[TimeSlotORM]:
        """
        Получить все слоты комнаты

        Args:
            room_id: ID комнаты
            include_inactive: Включать ли неактивные слоты

        Returns:
            list: Список слотов
        """

        query = select(TimeSlotORM).where(TimeSlotORM.room_id == room_id)

        if not include_inactive:
            query = query.where(TimeSlotORM.is_active == True)

        query = query.order_by(TimeSlotORM.start_time)
        return self.db.execute(query).scalars().all()

    def get_active_slots_by_room(self, room_id: int) -> list[TimeSlotORM]:
        """
        Получить активные слоты комнаты

        Args:
            room_id: ID комнаты

        Returns:
            list: Список активных слотов
        """

        return self.get_by_room(room_id, include_inactive=False)

    def check_overlap(
        self,
        room_id: int,
        start_time: time,
        end_time: time,
        day_of_week: int | None = None,
        exclude_id: int | None = None,
    ) -> TimeSlotORM | None:
        """
        Проверить пересечение слотов.

        Args:
            room_id: ID комнаты
            start_time: Время начала
            end_time: Время окончания
            day_of_week: День недели (если указан)
            exclude_id: ID слота для исключения (при обновлении)

        Returns:
            TimeSlotORM | None: Пересекающийся слот или None
        """

        query = select(TimeSlotORM).where(
            TimeSlotORM.room_id == room_id,
            TimeSlotORM.start_time < end_time,
            TimeSlotORM.end_time > start_time,
        )

        # Учитываем день недели
        if day_of_week is not None:
            query = query.where(
                or_(
                    TimeSlotORM.day_of_week == day_of_week,
                    TimeSlotORM.day_of_week.is_(None),
                )
            )

        if exclude_id:
            query = query.where(TimeSlotORM.id != exclude_id)

        return self.db.execute(query).scalar_one_or_none()

    def ensure_no_overlap(
        self,
        room_id: int,
        start_time: time,
        end_time: time,
        day_of_week: int | None = None,
        exclude_id: int | None = None,
    ) -> None:
        """
        Проверяет отсутствие пересечений и выбрасывает исключение при их наличии.

        Args:
            room_id: ID комнаты
            start_time: Время начала
            end_time: Время окончания
            day_of_week: День недели (если указан)
            exclude_id: ID слота для исключения (при обновлении)

        Raises:
            TimeSlotOverlapError: Если слот пересекается с существующим
        """

        overlapping = self.check_overlap(
            room_id, start_time, end_time, day_of_week, exclude_id
        )

        if overlapping:
            raise TimeSlotOverlapError(
                f"Слот {overlapping.start_time}-{overlapping.end_time} "
                f"пересекается с новым слотом {start_time}-{end_time}"
            )

    def get_slots_by_day(self, day_of_week: int) -> list[TimeSlotORM]:
        """
        Получить слоты для указанного дня недели

        Args:
            day_of_week: День недели (0=Понедельник, 6=Воскресенье)

        Returns:
            list: Список слотов
        """

        query = select(TimeSlotORM).where(
            or_(
                TimeSlotORM.day_of_week == day_of_week,
                TimeSlotORM.day_of_week.is_(None),
            ),
            TimeSlotORM.is_active == True,
        )
        query = query.order_by(TimeSlotORM.start_time)
        return self.db.execute(query).scalars().all()
