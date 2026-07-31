from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.models.user import UserORM
from app.repositories.user_repository import UserRepository
from app.api.dependencies.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/form")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserORM:
    """
    Зависимость для получения текущего аутентифицированного пользователя

    Извлекает JWT токен из заголовка Authorization, верифицирует его
    и возвращает пользователя.

    Args:
        token: JWT токен из заголовка
        db: Сессия БД

    Returns:
        UserORM: Текущий пользователь

    Raises:
        HTTPException: Если токен невалиден или пользователь не найден
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception

        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(int(user_id))

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт заблокирован. Обратитесь к администратору",
        )

    return user


def get_current_active_user(
    current_user: UserORM = Depends(get_current_user),
) -> UserORM:
    """
    Зависимость для получения активного пользователя.

    Проверяет, что пользователь активен (is_active=True).

    Args:
        current_user: Текущий пользователь из get_current_user

    Returns:
        UserORM: Активный пользователь

    Raises:
        HTTPException: Если пользователь неактивен
    """

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт заблокирован. Обратитесь к администратору",
        )
    return current_user


def get_current_admin(
    current_user: UserORM = Depends(get_current_active_user),
) -> UserORM:
    """
    Зависимость для получения администратора.

    Проверяет, что пользователь имеет роль администратора.

    Args:
        current_user: Текущий активный пользователь

    Returns:
        UserORM: Пользователь-администратор

    Raises:
        HTTPException: Если пользователь не администратор
    """

    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль администратора",
        )
    return current_user
