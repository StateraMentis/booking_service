from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_user_service, get_current_user, get_current_admin
from app.api.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserSelfUpdate,
)
from app.api.schemas.common import PaginationParams, PaginatedResponse
from app.services.user_service import UserService
from app.models.user import UserORM

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Получить информацию о себе",
    description="Возвращает данные текущего аутентифицированного пользователя",
    responses={
        200: {"description": "Данные пользователя", "model": UserResponse},
        401: {"description": "Пользователь не аутентифицирован"},
    },
)
def get_current_user_info(
    current_user: UserORM = Depends(get_current_user),
) -> UserResponse:
    """
    Возвращает информацию о текущем пользователе
    """

    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Обновить свои данные",
    description="Обновляет данные текущего пользователя",
    responses={
        200: {"description": "Данные обновлены", "model": UserResponse},
        400: {"description": "Некорректные данные"},
        401: {"description": "Пользователь не аутентифицирован"},
    },
)
def update_current_user(
    data: UserSelfUpdate,
    current_user: UserORM = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Обновляет данные текущего пользователя"""

    updated_user = user_service.update_user(
        current_user.id, data.model_dump(exclude_unset=True), is_admin=False
    )
    return UserResponse.model_validate(updated_user)


@router.get(
    "/",
    response_model=PaginatedResponse[UserListResponse],
    summary="Список пользователей (админ)",
    description="Возвращает список всех пользователей с пагинацией. Доступно только администратору.",
    dependencies=[Depends(get_current_admin)],
    responses={
        200: {"description": "Список пользователей"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
    },
)
def get_users(
    pagination: PaginationParams = Depends(),
    user_service: UserService = Depends(get_user_service),
) -> PaginatedResponse[UserListResponse]:
    """
    Получение списка пользователей (только для администраторов)

    - **page**: Номер страницы (по умолчанию 1)
    - **size**: Количество записей на странице (по умолчанию 20, максимум 100)
    """

    users, total = user_service.get_users(pagination.page, pagination.size)
    return PaginatedResponse(
        items=[UserListResponse.model_validate(u) for u in users],
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size,
    )


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя (админ)",
    description="Создает нового пользователя. Доступно только администратору.",
    dependencies=[Depends(get_current_admin)],
    responses={
        201: {"description": "Пользователь создан", "model": UserResponse},
        400: {"description": "Некорректные данные или пользователь уже существует"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
    },
)
def create_user(
    data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Создание нового пользователя (только для администраторов)
    """

    user = user_service.create_user(data)
    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Получить пользователя (админ)",
    description="Возвращает данные пользователя по ID. Доступно только администратору.",
    dependencies=[Depends(get_current_admin)],
    responses={
        200: {"description": "Данные пользователя", "model": UserResponse},
        404: {"description": "Пользователь не найден"},
    },
)
def get_user_by_id(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Получение пользователя по ID (только для администраторов)
    """

    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден",
        )
    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Обновить пользователя (админ)",
    description="Обновляет данные пользователя. Доступно только администратору.",
    dependencies=[Depends(get_current_admin)],
    responses={
        200: {"description": "Пользователь обновлен", "model": UserResponse},
        404: {"description": "Пользователь не найден"},
    },
)
def update_user(
    user_id: int,
    data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Обновление данных пользователя (только для администраторов)
    """

    updated_user = user_service.update_user(
        user_id, data.model_dump(exclude_unset=True), is_admin=True
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден",
        )
    return UserResponse.model_validate(updated_user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя (админ)",
    description="Удаляет пользователя. Доступно только администратору.",
    dependencies=[Depends(get_current_admin)],
    responses={
        204: {"description": "Пользователь удален"},
        404: {"description": "Пользователь не найден"},
        400: {"description": "Нельзя удалить самого себя"},
    },
)
def delete_user(
    user_id: int,
    current_user: UserORM = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> None:
    """
    Удаление пользователя (только для администраторов)
    """

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя удалить самого себя"
        )

    deleted = user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден",
        )
