from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    get_auth_service,
    get_current_user,
    get_user_service,
)
from app.api.schemas.auth import LoginRequest, TokenResponse
from app.api.schemas.common import ErrorResponse
from app.api.schemas.user import (
    UserCreate,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.models.user import UserORM

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
    description="Создает нового пользователя с ролью employee",
    responses={
        201: {"description": "Пользователь создан", "model": UserResponse},
        400: {"description": "Некорректные данные или пользователь уже существует"},
    },
)
def register(
    data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Создание нового пользователя
    """
    user = user_service.create_user(data)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Аутентификация пользователя",
    description="Получение JWT токена по логину и паролю",
    responses={
        200: {"description": "Успешная аутентификация", "model": TokenResponse},
        401: {"description": "Неверные учетные данные", "model": ErrorResponse},
        403: {"description": "Аккаунт заблокирован", "model": ErrorResponse},
    },
)
def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Аутентификация пользователя.

    - **username**: Имя пользователя
    - **password**: Пароль
    """
    user = auth_service.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт заблокирован. Обратитесь к администратору",
        )

    return auth_service.create_tokens(user.id, user.role)


# Ручка для Swagger UI, чтобы можно было тестировать аутентификацию через форму
# `include_in_schema=False` скрывает этот эндпоинт из документации
@router.post(
    "/login/form",
    response_model=TokenResponse,
    include_in_schema=False,
)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Аутентификация через form-data (для Swagger UI)
    """

    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return auth_service.create_tokens(user.id, user.role)
