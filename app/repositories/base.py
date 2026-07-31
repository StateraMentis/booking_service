from typing import TypeVar, Generic, Type
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.base import BaseORM

ModelType = TypeVar("ModelType", bound=BaseORM)


class BaseRepository(Generic[ModelType]):
    """
    Базовый репозиторий для CRUD операций с SQLAlchemy моделями

    Attributes:
        model: Класс модели SQLAlchemy
        db: Сессия базы данных
    """

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> ModelType | None:
        """
        Получить запись по ID
        """

        return self.db.get(self.model, id)

    def get_all(
        self, skip: int = 0, limit: int = 100, **filters
    ) -> tuple[list[ModelType], int]:
        """
        Получить список записей с пагинацией и фильтрацией.

        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            **filters: Фильтры для WHERE

        Returns:
            tuple: (список записей, общее количество)
        """

        query = select(self.model)

        for key, value in filters.items():
            if value is not None:
                query = query.where(getattr(self.model, key) == value)

        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0

        query = query.offset(skip).limit(limit)
        items = self.db.execute(query).scalars().all()

        return items, total

    def create(self, **data) -> ModelType:
        """
        Создать новую запись
        """

        instance = self.model(**data)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update(self, id: int, **data) -> ModelType | None:
        """
        Обновить запись
        """

        instance = self.get_by_id(id)
        if not instance:
            return None

        for key, value in data.items():
            if value is not None:
                setattr(instance, key, value)

        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, id: int) -> bool:
        """
        Удалить запись
        """

        instance = self.get_by_id(id)
        if not instance:
            return False

        self.db.delete(instance)
        self.db.commit()
        return True

    def exists(self, **filters) -> bool:
        """
        Проверить существование записи по фильтрам
        """

        query = select(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        return self.db.execute(query).first() is not None
