from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_time_slot_service,
    get_current_admin,
    get_current_user,
)
from app.api.schemas.timeslot import TimeSlotCreate, TimeSlotUpdate, TimeSlotResponse
from app.services.timeslot_service import TimeSlotService
from app.models import UserORM

router = APIRouter(prefix="/time-slots", tags=["Time-slots"])


@router.post(
    "/",
    response_model=TimeSlotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать временной слот (админ)",
    description="Создает новый временной слот для комнаты. Доступно только администратору.",
    dependencies=[Depends(get_current_admin)],
    responses={
        201: {"description": "Слот создан", "model": TimeSlotResponse},
        400: {"description": "Некорректные данные"},
        404: {"description": "Комната не найдена"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
        409: {"description": "Слот пересекается с существующим"},
    },
)
def create_time_slot(
    data: TimeSlotCreate,
    time_slot_service: TimeSlotService = Depends(get_time_slot_service),
) -> TimeSlotResponse:
    """
    Создание временного слота для комнаты (только для администраторов)
    """

    slot = time_slot_service.create_time_slot(data)
    return TimeSlotResponse.model_validate(slot)


@router.get(
    "/rooms/{room_id}",
    response_model=list[TimeSlotResponse],
    summary="Получить все слоты комнаты",
    description="Возвращает все временные слоты для указанной комнаты",
    responses={
        200: {"description": "Список слотов"},
        404: {"description": "Комната не найдена"},
    },
)
def get_room_time_slots(
    room_id: int,
    include_inactive: bool = False,
    time_slot_service: TimeSlotService = Depends(get_time_slot_service),
    current_user: UserORM = Depends(get_current_user),
) -> list[TimeSlotResponse]:
    """
    Получение всех временных слотов для комнаты

    - **include_inactive**: Включать неактивные слоты (по умолчанию False)
    """

    slots = time_slot_service.get_room_slots(room_id, include_inactive)
    return [TimeSlotResponse.model_validate(s) for s in slots]


@router.put(
    "/{slot_id}",
    response_model=TimeSlotResponse,
    summary="Обновить временной слот (админ)",
    description="Обновляет данные временного слота. Доступно только администратору.",
    dependencies=[Depends(get_current_admin)],
    responses={
        200: {"description": "Слот обновлен", "model": TimeSlotResponse},
        404: {"description": "Слот не найден"},
        400: {
            "description": "Некорректные данные или слот пересекается с существующим"
        },
    },
)
def update_time_slot(
    slot_id: int,
    data: TimeSlotUpdate,
    time_slot_service: TimeSlotService = Depends(get_time_slot_service),
) -> TimeSlotResponse:
    """
    Обновление временного слота (только для администраторов)
    """

    slot = time_slot_service.update_time_slot(
        slot_id, data.model_dump(exclude_unset=True)
    )
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Временной слот с ID {slot_id} не найден",
        )
    return TimeSlotResponse.model_validate(slot)


@router.delete(
    "/{slot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить временной слот (админ)",
    description="Удаляет временной слот. Доступно только администратору.",
    dependencies=[Depends(get_current_admin)],
    responses={
        204: {"description": "Слот удален"},
        404: {"description": "Слот не найден"},
        409: {"description": "Невозможно удалить слот с активными бронированиями"},
    },
)
def delete_time_slot(
    slot_id: int,
    time_slot_service: TimeSlotService = Depends(get_time_slot_service),
) -> None:
    """
    Удаление временного слота (только для администраторов)
    """

    deleted = time_slot_service.delete_time_slot(slot_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Временной слот с ID {slot_id} не найден",
        )
