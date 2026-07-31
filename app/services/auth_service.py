from datetime import timedelta
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.core.security import (
    verify_password,
    create_access_token,
)
from app.core.config import settings
from app.exceptions import (
    InvalidCredentialsError,
    UserInactiveError,
    UserNotFoundError,
    ValidationError,
)
from app.models import UserORM


class AuthService:
    """
    Сервис аутентификации
    """

    def __init__(self, db: Session, user_repo: UserRepository):
        self.db = db
        self.user_repo = user_repo

    def authenticate_user(self, username: str, password: str) -> UserORM:
        """
        Аутентифицировать пользователя

        Args:
            username: Имя пользователя или email
            password: Пароль

        Returns:
            UserORM: Аутентифицированный пользователь

        Raises:
            InvalidCredentialsError: Неверные учетные данные
            UserInactiveError: Пользователь неактивен
            UserNotFoundError: Пользователь не найден
        """

        user = self.user_repo.get_by_username_or_email(username)

        if not user:
            raise UserNotFoundError("Пользователь не найден")

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Неверное имя пользователя или пароль")

        if not user.is_active:
            raise UserInactiveError("Аккаунт заблокирован. Обратитесь к администратору")

        return user

    def create_tokens(self, user_id: int, role: str) -> dict:
        """
        Создать JWT токены

        Args:
            user_id: ID пользователя
            role: Роль пользователя

        Returns:
            dict: Токены доступа и обновления
        """

        access_token = create_access_token(
            data={"sub": str(user_id), "role": role},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user_id": user_id,
            "role": role,
        }

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
        confirm_password: str,
    ) -> None:
        """
        Сменить пароль пользователя

        Args:
            user_id: ID пользователя
            old_password: Старый пароль
            new_password: Новый пароль
            confirm_password: Подтверждение нового пароля

        Raises:
            UserNotFoundError: Пользователь не найден
            InvalidCredentialsError: Неверный старый пароль
            ValidationError: Пароли не совпадают
        """

        if new_password != confirm_password:
            raise ValidationError("Пароли не совпадают")

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("Пользователь не найден")

        if not verify_password(old_password, user.password_hash):
            raise InvalidCredentialsError("Неверный старый пароль")

        self.user_repo.update_password(user_id, new_password)
