from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import time
from app.api.schemas.common import BaseResponse
from app.exceptions import TimeSlotIncorrect


class TimeSlotCreate(BaseModel):
    """
    Схема для создания временного слота
    """

    start_time: time = Field(..., description="Время начала слота (HH:MM)")
    end_time: time = Field(..., description="Время окончания слота (HH:MM)")
    day_of_week: int | None = Field(
        None,
        ge=0,
        le=6,
        description="День недели (0=понедельник, 6=воскресенье). Если None — слот доступен ежедневно",
    )
    is_active: bool = Field(True, description="Флаг активности слота")
    room_id: int = Field(..., description="Уникальный идентификатор комнаты")

    @field_validator("end_time")
    @classmethod
    def validate_time_range(cls, v: time, info) -> time:
        """
        Проверяет, что время окончания больше времени начала
        """

        start_time = info.data.get("start_time")
        if start_time and v <= start_time:
            raise TimeSlotIncorrect("Время окончания должно быть больше времени начала")
        return v

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, v: time) -> time:
        """
        Проверяет, что время начала не слишком рано и не слишком поздно
        """

        min_time = time(6, 0)  # 6:00
        max_time = time(23, 0)  # 23:00
        if v < min_time or v > max_time:
            raise TimeSlotIncorrect("Время начала должно быть между 6:00 и 23:00")
        return v


class TimeSlotUpdate(BaseModel):
    """
    Схема для обновления временного слота
    """

    start_time: time | None = Field(None, description="Время начала слота")
    end_time: time | None = Field(None, description="Время окончания слота")
    day_of_week: int | None = Field(None, ge=0, le=6, description="День недели")
    is_active: bool | None = Field(None, description="Флаг активности слота")
    room_id: int | None = Field(None, description="Уникальный идентификатор комнаты")

    @field_validator("end_time")
    @classmethod
    def validate_time_range(cls, v: time | None, info) -> time | None:
        if v is None:
            return v
        start_time = info.data.get("start_time")
        if start_time and v <= start_time:
            raise TimeSlotIncorrect("Время окончания должно быть больше времени начала")
        return v


class TimeSlotResponse(BaseResponse):
    """
    Схема ответа с данными временного слота
    """

    room_id: int = Field(..., description="ID комнаты")
    start_time: time = Field(..., description="Время начала слота")
    end_time: time = Field(..., description="Время окончания слота")
    day_of_week: int | None = Field(None, description="День недели (0=понедельник)")
    is_active: bool = Field(..., description="Флаг активности слота")
    room_id: int = Field(..., description="Уникальный идентификатор комнаты")

    @property
    def display_name(self) -> str:
        """
        Человекочитаемое отображение слота
        """
        day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        day_str = (
            f"{day_names[self.day_of_week]} " if self.day_of_week is not None else ""
        )
        return f"{day_str}{self.start_time.strftime('%H:%M')}–{self.end_time.strftime('%H:%M')}"

    model_config = ConfigDict(from_attributes=True)
