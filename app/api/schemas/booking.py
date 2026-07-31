from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime
from app.enums import BookingStatus
from app.api.schemas import (
    UserListResponse,
    TimeSlotResponse,
    RoomResponse,
    BaseResponse,
)
from app.exceptions import BookingDateInPastError


class BookingCreate(BaseModel):
    """
    Схема для создания бронирования
    """

    room_id: int = Field(..., gt=0, description="ID комнаты")
    time_slot_id: int = Field(..., gt=0, description="ID временного слота")
    booking_date: date = Field(..., description="Дата бронирования")
    description: str | None = Field(
        None, max_length=500, description="Описание встречи"
    )

    @field_validator("booking_date")
    @classmethod
    def validate_date(cls, v: date) -> date:
        """
        Проверяет, что дата не в прошлом и не слишком далеко в будущем
        """

        today = date.today()
        max_future = today.replace(year=today.year + 1)

        if v < today:
            raise BookingDateInPastError("Нельзя бронировать на прошедшую дату")
        if v > max_future:
            raise BookingDateInPastError("Нельзя бронировать более чем на год вперед")
        return v


class BookingUpdate(BaseModel):
    """
    Схема для обновления бронирования
    """

    booking_date: date | None = Field(None, description="Новая дата бронирования")
    time_slot_id: int | None = Field(
        None, gt=0, description="Новый ID временного слота"
    )
    description: str | None = Field(None, max_length=500, description="Новое описание")

    @field_validator("booking_date")
    @classmethod
    def validate_date(cls, v: date | None) -> date | None:
        if v is None:
            return v
        today = date.today()
        if v < today:
            raise BookingDateInPastError("Нельзя бронировать на прошедшую дату")
        return v


class BookingCancel(BaseModel):
    """
    Схема для отмены бронирования (причина опционально)
    """

    reason: str | None = Field(None, max_length=500, description="Причина отмены")


class BookingResponse(BaseResponse):
    """
    Схема ответа с данными бронирования
    """

    room_id: int = Field(..., description="ID комнаты")
    room: RoomResponse | None = Field(None, description="Данные комнаты")
    time_slot_id: int = Field(..., description="ID временного слота")
    time_slot: TimeSlotResponse | None = Field(
        None, description="Данные временного слота"
    )
    user_id: int = Field(..., description="ID пользователя")
    user: UserListResponse | None = Field(None, description="Данные пользователя")
    booking_date: date = Field(..., description="Дата бронирования")
    description: str | None = Field(None, description="Описание встречи")
    status: BookingStatus = Field(..., description="Статус бронирования")
    cancelled_at: datetime | None = Field(None, description="Дата и время отмены")
    cancelled_by_id: int | None = Field(
        None, description="ID пользователя, отменившего бронирование"
    )
    cancelled_by: UserListResponse | None = Field(
        None, description="Данные пользователя, отменившего бронь"
    )

    model_config = ConfigDict(from_attributes=True)


class BookingHistoryResponse(BaseModel):
    """
    Схема для истории бронирований пользователя
    """

    total_bookings: int = Field(..., description="Общее количество бронирований")
    active_bookings: int = Field(..., description="Количество активных бронирований")
    cancelled_bookings: int = Field(
        ..., description="Количество отмененных бронирований"
    )
    bookings: list[BookingResponse] = Field(..., description="Список бронирований")
