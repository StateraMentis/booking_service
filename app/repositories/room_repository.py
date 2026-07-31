from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func

from app.repositories.base import BaseRepository
from app.models.room import MeetingRoomORM


class RoomRepository(BaseRepository[MeetingRoomORM]):
    """
    Репозиторий для работы с переговорными комнатами
    """

    def __init__(self, db: Session):
        super().__init__(MeetingRoomORM, db)

    def get_by_name(self, name: str) -> MeetingRoomORM | None:
        """
        Получить комнату по названию

        Args:
            name: Название комнаты

        Returns:
            MeetingRoomORM | None: Комната или None, если не найдена
        """
        return self.db.execute(
            select(MeetingRoomORM).where(MeetingRoomORM.name == name)
        ).scalar_one_or_none()

    def get_active_rooms(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[MeetingRoomORM], int]:
        """
        Получить все активные комнаты

        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            tuple: (список комнат, общее количество)
        """

        return self.get_all(skip=skip, limit=limit, is_active=True)

    def get_rooms_with_min_capacity(
        self,
        capacity: int,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[MeetingRoomORM], int]:
        """
        Получить комнаты с вместимостью не меньше указанной

        Args:
            capacity: Минимальная вместимость
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            tuple: (список комнат, общее количество)
        """

        query = select(MeetingRoomORM).where(
            MeetingRoomORM.capacity >= capacity, MeetingRoomORM.is_active == True
        )

        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0

        query = query.offset(skip).limit(limit)
        items = self.db.execute(query).scalars().all()

        return items, total

    def search_rooms(
        self,
        search: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[MeetingRoomORM], int]:
        """
        Поиск комнат по названию или описанию

        Args:
            search: Строка поиска
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            tuple: (список комнат, общее количество)
        """

        query = select(MeetingRoomORM)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    MeetingRoomORM.name.ilike(search_pattern),
                    MeetingRoomORM.description.ilike(search_pattern),
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0

        query = query.offset(skip).limit(limit)
        items = self.db.execute(query).scalars().all()

        return items, total
