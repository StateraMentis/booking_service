from sqlalchemy.orm import Session
from sqlalchemy import select, or_, func

from app.repositories.base import BaseRepository
from app.models.user import UserORM, UserRole
from app.core.security import get_password_hash


class UserRepository(BaseRepository[UserORM]):
    """
    Репозиторий для работы с пользователями
    """

    def __init__(self, db: Session):
        super().__init__(UserORM, db)

    def get_by_username(self, username: str) -> UserORM | None:
        """
        Получить пользователя по имени

        Args:
            username: Имя пользователя

        Returns:
            UserORM | None: Пользователь или None, если не найден
        """

        return self.db.execute(
            select(UserORM).where(UserORM.username == username.lower())
        ).scalar_one_or_none()

    def get_by_email(self, email: str) -> UserORM | None:
        """
        Получить пользователя по email

        Args:
            email: Email пользователя

        Returns:
            UserORM | None: Пользователь или None, если не найден
        """

        return self.db.execute(
            select(UserORM).where(UserORM.email == email)
        ).scalar_one_or_none()

    def get_by_username_or_email(self, login: str) -> UserORM | None:
        """
        Получить пользователя по имени или email

        Args:
            login: Имя пользователя или email

        Returns:
            UserORM | None: Пользователь или None, если не найден
        """
        return self.db.execute(
            select(UserORM).where(
                or_(UserORM.username == login.lower(), UserORM.email == login)
            )
        ).scalar_one_or_none()

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str | None = None,
        role: UserRole = UserRole.EMPLOYEE,
    ) -> UserORM:
        """
        Создать нового пользователя с хешированным паролем

        Args:
            username: Имя пользователя
            email: Email пользователя
            password: Пароль пользователя
            full_name: Полное имя пользователя (необязательно)
            role: Роль пользователя (по умолчанию EMPLOYEE)

        Returns:
            UserORM: Созданный пользователь
        """

        password_hash = get_password_hash(password)
        return self.create(
            username=username.lower(),
            email=email.lower(),
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            is_active=True,
        )

    def update_password(self, user_id: int, new_password: str) -> UserORM | None:
        """
        Обновить пароль пользователя.

        Args:
            user_id: ID пользователя
            new_password: Новый пароль

        Returns:
            UserORM | None: Обновленный пользователь или None, если не найден
        """

        password_hash = get_password_hash(new_password)
        return self.update(user_id, password_hash=password_hash)

    def get_admins(self) -> list[UserORM]:
        """
        Получить всех администраторов.

        Returns:
            list: Список администраторов
        """
        return (
            self.db.execute(
                select(UserORM).where(
                    UserORM.role == UserRole.ADMIN, UserORM.is_active == True
                )
            )
            .scalars()
            .all()
        )

    def search_users(
        self,
        search: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[UserORM], int]:
        """
        Поиск пользователей по имени, email или полному имени.

        Args:
            search: Поисковый запрос
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей

        Returns:
            tuple: (список пользователей, общее количество)
        """

        query = select(UserORM)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    UserORM.username.ilike(search_pattern),
                    UserORM.email.ilike(search_pattern),
                    UserORM.full_name.ilike(search_pattern),
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = self.db.execute(count_query).scalar() or 0

        query = query.offset(skip).limit(limit)
        items = self.db.execute(query).scalars().all()

        return items, total
