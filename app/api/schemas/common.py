from typing import TypeVar, Generic
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

T = TypeVar("T")


class BaseResponse(BaseModel):
    """
    Базовая схема ответа с общими полями
    """

    id: int = Field(..., description="Уникальный идентификатор")
    added_at: datetime = Field(..., description="Дата и время создания")
    updated_at: datetime = Field(..., description="Дата и время последнего обновления")

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """
    Параметры пагинации
    """

    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(20, ge=1, le=100, description="Количество записей на странице")
    sort: str | None = Field(
        None, description="Поле для сортировки (например: 'added_at', '-added_at')"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Схема ответа с пагинацией
    """

    items: list[T] = Field(..., description="Список элементов")
    total: int = Field(..., description="Общее количество элементов")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Размер страницы")
    pages: int = Field(..., description="Общее количество страниц")


class ErrorResponse(BaseModel):
    """
    Схема ошибки
    """

    detail: str = Field(..., description="Описание ошибки")
    status_code: int = Field(..., description="HTTP статус-код")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Время возникновения ошибки"
    )
    path: str | None = Field(None, description="Путь, на котором возникла ошибка")
