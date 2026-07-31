from datetime import time, datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.api.schemas.common import BaseResponse
from app.api.schemas.timeslot import TimeSlotResponse


class RoomCreate(BaseModel):
    """
    Схема для создания комнаты
    """

    name: str = Field(..., min_length=1, max_length=100, description="Название комнаты")
    description: str | None = Field(
        None, max_length=500, description="Описание комнаты"
    )
    capacity: int = Field(
        2, ge=1, le=50, description="Вместимость комнаты (количество человек)"
    )
    is_active: bool = Field(True, description="Флаг доступности комнаты")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Проверяет, что имя не содержит специальных символов."""
        if any(c in v for c in "<>{}[]|\\/"):
            raise ValueError("Название комнаты содержит недопустимые символы")
        return v.strip()


class RoomUpdate(BaseModel):
    """
    Схема для обновления комнаты
    """

    name: str | None = Field(
        None, min_length=1, max_length=100, description="Название комнаты"
    )
    description: str | None = Field(
        None, max_length=500, description="Описание комнаты"
    )
    capacity: int | None = Field(None, ge=1, le=50, description="Вместимость комнаты")
    is_active: bool | None = Field(None, description="Флаг доступности комнаты")


class RoomResponse(BaseResponse):
    """
    Схема ответа с данными комнаты
    """

    name: str = Field(..., description="Название комнаты")
    description: str | None = Field(None, description="Описание комнаты")
    capacity: int = Field(..., description="Вместимость комнаты")
    is_active: bool = Field(..., description="Флаг доступности комнаты")
    time_slots: list[TimeSlotResponse] = Field(
        default_factory=list, description="Список временных слотов комнаты"
    )

    model_config = ConfigDict(from_attributes=True)


class RoomAvailabilityResponse(BaseModel):
    """
    Схема ответа с доступностью комнаты на дату
    """

    room_id: int = Field(..., description="ID комнаты")
    room_name: str = Field(..., description="Название комнаты")
    capacity: int = Field(..., description="Вместимость комнаты")
    date: str = Field(..., description="Дата проверки")
    available_slots: list[TimeSlotResponse] = Field(
        ..., description="Список доступных слотов"
    )
    total_slots: int = Field(..., description="Общее количество слотов")
    booked_slots: int = Field(..., description="Количество забронированных слотов")
    is_fully_booked: bool = Field(..., description="Все ли слоты забронированы")
