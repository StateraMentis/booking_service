from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import date

from app.api.dependencies import get_room_service, get_current_user, get_current_admin
from app.api.schemas.room import (
    RoomCreate,
    RoomUpdate,
    RoomResponse,
    RoomAvailabilityResponse,
)
from app.api.schemas.common import PaginationParams, PaginatedResponse
from app.services.room_service import RoomService
from app.models.user import UserORM

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.post(
    "/",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать комнату (админ)",
    description="Создает новую переговорную комнату. Доступно только администратору.",
    dependencies=[Depends(get_current_admin)],
    responses={
        201: {"description": "Комната создана", "model": RoomResponse},
        400: {"description": "Комната с таким названием уже существует"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
    },
)
def create_room(
    data: RoomCreate,
    room_service: RoomService = Depends(get_room_service),
    current_user: UserORM = Depends(get_current_user),
) -> RoomResponse:
    """
    Создание новой комнаты (только для администраторов)
    """

    room = room_service.create_room(data)
    return RoomResponse.model_validate(room)


@router.get(
    "/",
    response_model=PaginatedResponse[RoomResponse],
    summary="Список комнат",
    description="Возвращает список всех активных комнат с пагинацией",
    responses={
        200: {"description": "Список комнат"},
    },
)
def get_rooms(
    pagination: PaginationParams = Depends(),
    room_service: RoomService = Depends(get_room_service),
    current_user: UserORM = Depends(get_current_user),
) -> PaginatedResponse[RoomResponse]:
    """
    Получение списка всех активных комнат

    - **page**: Номер страницы (по умолчанию 1)
    - **size**: Количество записей на странице (по умолчанию 20, максимум 100)
    """

    rooms, total = room_service.get_rooms(pagination.page, pagination.size)
    return PaginatedResponse(
        items=[RoomResponse.model_validate(r) for r in rooms],
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size,
    )


@router.get(
    "/{room_id}",
    response_model=RoomResponse,
    summary="Получить комнату",
    description="Возвращает данные комнаты по ID",
    responses={
        200: {"description": "Данные комнаты", "model": RoomResponse},
        404: {"description": "Комната не найдена"},
    },
)
def get_room_by_id(
    room_id: int,
    room_service: RoomService = Depends(get_room_service),
    current_user: UserORM = Depends(get_current_user),
) -> RoomResponse:
    """
    Получение комнаты по ID
    """

    room = room_service.get_room_by_id(room_id)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комната с ID {room_id} не найдена",
        )
    return RoomResponse.model_validate(room)


@router.put(
    "/{room_id}",
    response_model=RoomResponse,
    summary="Обновить комнату (админ)",
    description="Обновляет данные комнаты. Доступно только администратору.",
    dependencies=[Depends(get_current_admin)],
    responses={
        200: {"description": "Комната обновлена", "model": RoomResponse},
        404: {"description": "Комната не найдена"},
        409: {"description": "Комната с таким названием уже существует"},
    },
)
def update_room(
    room_id: int,
    data: RoomUpdate,
    room_service: RoomService = Depends(get_room_service),
    current_user: UserORM = Depends(get_current_user),
) -> RoomResponse:
    """
    Обновление данных комнаты (только для администраторов)
    """

    room = room_service.update_room(room_id, data.model_dump(exclude_unset=True))
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комната с ID {room_id} не найдена",
        )
    return RoomResponse.model_validate(room)


@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить комнату (админ)",
    description="Удаляет комнату. Доступно только администратору.",
    dependencies=[Depends(get_current_admin)],
    responses={
        204: {"description": "Комната удалена"},
        404: {"description": "Комната не найдена"},
        409: {"description": "Невозможно удалить комнату с активными бронированиями"},
    },
)
def delete_room(
    room_id: int,
    room_service: RoomService = Depends(get_room_service),
    current_user: UserORM = Depends(get_current_user),
) -> None:
    """
    Удаление комнаты (только для администраторов)
    """

    deleted = room_service.delete_room(room_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комната с ID {room_id} не найдена",
        )


@router.get(
    "/{room_id}/availability",
    response_model=RoomAvailabilityResponse,
    summary="Проверить доступность комнаты",
    description="Возвращает доступные слоты для комнаты на указанную дату",
    responses={
        200: {"description": "Доступность комнаты"},
        404: {"description": "Комната не найдена"},
        400: {"description": "Некорректная дата"},
    },
)
def check_room_availability(
    room_id: int,
    date_str: str = Query(..., description="Дата в формате YYYY-MM-DD"),
    room_service: RoomService = Depends(get_room_service),
    current_user: UserORM = Depends(get_current_user),
) -> RoomAvailabilityResponse:
    """
    Проверка доступности комнаты на указанную дату.

    - **date_str**: Дата в формате YYYY-MM-DD
    """

    try:
        check_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат даты. Используйте YYYY-MM-DD",
        )

    availability = room_service.check_availability(room_id, check_date)
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комната с ID {room_id} не найдена",
        )

    return availability
