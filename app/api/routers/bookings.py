from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import date

from app.api.dependencies import (
    get_booking_service,
    get_current_admin,
    get_current_user,
)
from app.api.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingCancel,
    BookingResponse,
    BookingHistoryResponse,
)
from app.api.schemas.common import PaginationParams, PaginatedResponse
from app.services.booking_service import BookingService
from app.models.user import UserORM

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать бронирование",
    description="Создает новое бронирование для текущего пользователя",
    responses={
        201: {"description": "Бронирование создано", "model": BookingResponse},
        400: {"description": "Некорректные данные"},
        401: {"description": "Пользователь не аутентифицирован"},
        404: {"description": "Комната или слот не найдены"},
        409: {"description": "Слот уже забронирован"},
    },
)
def create_booking(
    data: BookingCreate,
    current_user: UserORM = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingResponse:
    """
    Создание нового бронирования.

    - **room_id**: ID комнаты
    - **time_slot_id**: ID временного слота
    - **date**: Дата бронирования
    - **description**: Описание встречи (опционально)
    """
    booking = booking_service.create_booking(data, current_user.id)
    return BookingResponse.model_validate(booking)


@router.get(
    "/my",
    response_model=PaginatedResponse[BookingResponse],
    summary="Мои бронирования",
    description="Возвращает список бронирований текущего пользователя с пагинацией",
    responses={
        200: {"description": "Список бронирований"},
        401: {"description": "Пользователь не аутентифицирован"},
    },
)
def get_my_bookings(
    pagination: PaginationParams = Depends(),
    status_filter: str | None = Query(
        None, description="Фильтр по статусу (active, cancelled)"
    ),
    date_from: date | None = Query(None, description="Начальная дата (YYYY-MM-DD)"),
    date_to: date | None = Query(None, description="Конечная дата (YYYY-MM-DD)"),
    current_user: UserORM = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
) -> PaginatedResponse[BookingResponse]:
    """
    Получение бронирований текущего пользователя.

    - **page**: Номер страницы
    - **size**: Количество записей на странице
    - **status_filter**: Фильтр по статусу (active, cancelled)
    - **date_from**: Фильтр по дате (от)
    - **date_to**: Фильтр по дате (до)
    """
    bookings, total = booking_service.get_user_bookings(
        current_user.id,
        pagination.page,
        pagination.size,
        status_filter,
        date_from,
        date_to,
    )

    return PaginatedResponse(
        items=[BookingResponse.model_validate(b) for b in bookings],
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size,
    )


@router.get(
    "/my/history",
    response_model=BookingHistoryResponse,
    summary="История бронирований",
    description="Возвращает статистику и историю бронирований текущего пользователя",
    responses={
        200: {"description": "История бронирований"},
        401: {"description": "Пользователь не аутентифицирован"},
    },
)
def get_my_booking_history(
    limit: int = Query(50, ge=1, le=100, description="Количество записей в истории"),
    current_user: UserORM = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingHistoryResponse:
    """
    Получение истории бронирований текущего пользователя с агрегированной статистикой.
    """
    return booking_service.get_user_booking_history(current_user.id, limit)


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Получить бронирование",
    description="Возвращает данные бронирования по ID (с проверкой прав доступа)",
    responses={
        200: {"description": "Данные бронирования", "model": BookingResponse},
        404: {"description": "Бронирование не найдено"},
        403: {"description": "Нет доступа к этому бронированию"},
    },
)
def get_booking_by_id(
    booking_id: int,
    current_user: UserORM = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingResponse:
    """
    Получение бронирования по ID.

    Доступно:
    - Автору бронирования
    - Администратору
    """
    booking = booking_service.get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование с ID {booking_id} не найдено",
        )

    if booking.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет доступа к этому бронированию",
        )

    return BookingResponse.model_validate(booking)


@router.put(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Обновить бронирование",
    description="Обновляет данные бронирования (только для автора)",
    responses={
        200: {"description": "Бронирование обновлено", "model": BookingResponse},
        400: {"description": "Некорректные данные"},
        403: {"description": "Нет прав на изменение"},
        404: {"description": "Бронирование не найдено"},
        409: {"description": "Конфликт: слот уже занят"},
    },
)
def update_booking(
    booking_id: int,
    data: BookingUpdate,
    current_user: UserORM = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
) -> BookingResponse:
    """
    Обновление бронирования (только для автора бронирования).

    Можно изменить дату, слот или описание.
    """
    booking = booking_service.update_booking(
        booking_id,
        data.model_dump(exclude_unset=True),
        current_user.id,
        is_admin=current_user.role == "admin",
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование с ID {booking_id} не найдено",
        )
    return BookingResponse.model_validate(booking)


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отменить бронирование",
    description="Отменяет бронирование. Сотрудник может отменить только свои брони, администратор - любые.",
    responses={
        204: {"description": "Бронирование отменено"},
        403: {"description": "Нет прав на отмену"},
        404: {"description": "Бронирование не найдено"},
        409: {"description": "Бронирование уже отменено"},
    },
)
def cancel_booking(
    booking_id: int,
    data: BookingCancel | None = None,
    current_user: UserORM = Depends(get_current_user),
    booking_service: BookingService = Depends(get_booking_service),
) -> None:
    """
    Отмена бронирования.

    - Сотрудник может отменить только свои бронирования
    - Администратор может отменить любые бронирования
    """
    booking = booking_service.get_booking_by_id(
        booking_id,
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование с ID {booking_id} не найдено",
        )

    if booking.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Бронирование уже отменено"
        )

    booking_service.cancel_booking(
        booking_id, current_user.id, current_user.role == "admin"
    )


@router.get(
    "/admin/all",
    response_model=PaginatedResponse[BookingResponse],
    summary="Все бронирования (админ)",
    description="Возвращает список всех бронирований с пагинацией. Доступно только администратору.",
    dependencies=[Depends(get_current_admin)],
    responses={
        200: {"description": "Список всех бронирований"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
    },
)
def get_all_bookings(
    pagination: PaginationParams = Depends(),
    user_id: int | None = Query(None, description="Фильтр по пользователю"),
    room_id: int | None = Query(None, description="Фильтр по комнате"),
    status_filter: str | None = Query(None, description="Фильтр по статусу"),
    date_from: date | None = Query(None, description="Начальная дата"),
    date_to: date | None = Query(None, description="Конечная дата"),
    booking_service: BookingService = Depends(get_booking_service),
) -> PaginatedResponse[BookingResponse]:
    """
    Получение всех бронирований (только для администраторов).

    Доступна фильтрация по:
    - Пользователю (user_id)
    - Комнате (room_id)
    - Статусу (status_filter)
    - Диапазону дат (date_from, date_to)
    """
    bookings, total = booking_service.get_all_bookings(
        pagination.page,
        pagination.size,
        user_id=user_id,
        room_id=room_id,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
    )

    return PaginatedResponse(
        items=[BookingResponse.model_validate(b) for b in bookings],
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(total + pagination.size - 1) // pagination.size,
    )
