from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.api.schemas.user import UserCreate
from app.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    ValidationError,
)
from app.models import UserORM


class UserService:
    """
    Сервис для управления пользователями
    """

    def __init__(self, db: Session, user_repo: UserRepository):
        self.db = db
        self.user_repo = user_repo

    def get_user_by_id(self, user_id: int) -> UserORM | None:
        """
        Получить пользователя по ID

        Args:
            user_id: ID пользователя

        Returns:
            UserORM | None: Пользователь или None, если не найден
        """

        return self.user_repo.get_by_id(user_id)

    def get_users(self, page: int = 1, size: int = 20) -> tuple[list[UserORM], int]:
        """
        Получить список пользователей с пагинацией

        Args:
            page: Номер страницы
            size: Количество пользователей на странице

        Returns:
            tuple: Список пользователей и общее количество
        """

        skip = (page - 1) * size
        return self.user_repo.get_all(skip=skip, limit=size)

    def create_user(self, data: UserCreate) -> UserORM:
        """
        Создать нового пользователя

        Args:
            data: Данные для создания пользователя

        Returns:
            UserORM: Созданный пользователь

        Raises:
            UserAlreadyExistsError: Пользователь уже существует
        """

        if self.user_repo.get_by_username(data.username):
            raise UserAlreadyExistsError("Пользователь с таким именем уже существует")

        if self.user_repo.get_by_email(data.email):
            raise UserAlreadyExistsError("Пользователь с таким email уже существует")

        return self.user_repo.create_user(
            username=data.username,
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            role=data.role,
        )

    def update_user(
        self,
        user_id: int,
        data: dict,
        is_admin: bool = False,
    ) -> UserORM | None:
        """
        Обновить пользователя

        Args:
            user_id: ID пользователя
            data: Данные для обновления
            is_admin: Является ли текущий пользователь админом

        Returns:
            UserORM | None: Обновленный пользователь или None, если не найден

        Raises:
            UserNotFoundError: Пользователь не найден
            UserAlreadyExistsError: Конфликт уникальности
            ValidationError: Некорректные данные
        """

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")

        if "username" in data:
            existing = self.user_repo.get_by_username(data["username"])
            if existing and existing.id != user_id:
                raise UserAlreadyExistsError(
                    "Пользователь с таким именем уже существует"
                )

        if "email" in data:
            existing = self.user_repo.get_by_email(data["email"])
            if existing and existing.id != user_id:
                raise UserAlreadyExistsError(
                    "Пользователь с таким email уже существует"
                )

        if "role" in data and not is_admin:
            raise ValidationError("Только администратор может менять роль пользователя")

        return self.user_repo.update(user_id, **data)

    def delete_user(self, user_id: int) -> bool:
        """
        Удалить пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            bool: True, если пользователь удален, False в противном случае
        """

        return self.user_repo.delete(user_id)

    def search_users(
        self,
        search: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[UserORM], int]:
        """
        Поиск пользователей.

        Args:
            search: Поисковый запрос
            page: Номер страницы
            size: Количество пользователей на странице

        Returns:
            tuple: Список пользователей и общее количество
        """

        skip = (page - 1) * size
        return self.user_repo.search_users(search, skip, size)
