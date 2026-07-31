from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from app.enums import UserRole
from app.api.schemas.common import BaseResponse


class UserCreate(BaseModel):
    """
    Схема для создания пользователя
    """

    username: str = Field(
        ..., min_length=3, max_length=50, description="Имя пользователя"
    )
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=6, max_length=100, description="Пароль")
    full_name: str | None = Field(None, max_length=100, description="Полное имя")
    role: UserRole = Field(UserRole.EMPLOYEE, description="Роль пользователя")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v.isalnum() and "_" not in v:
            raise ValueError(
                "Имя пользователя может содержать только буквы, цифры и символ подчеркивания"
            )
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Валидация пароля перед хешированием
        """

        byte_length = len(v.encode("utf-8"))
        if byte_length > 72:
            raise ValueError(
                f"Пароль слишком длинный ({byte_length} байт). "
                "Максимальная длина 72 байта"
            )

        if len(v) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")

        if not any(c.isupper() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну заглавную букву")

        if not any(c.islower() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну строчную букву")

        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")

        return v


class UserUpdate(BaseModel):
    """
    Схема для обновления пользователя
    """

    email: EmailStr | None = Field(None, description="Email пользователя")
    full_name: str | None = Field(None, max_length=100, description="Полное имя")
    is_active: bool | None = Field(None, description="Флаг активности")
    role: UserRole | None = Field(
        None, description="Роль пользователя (только для админа)"
    )


class UserResponse(BaseResponse):
    """
    Схема ответа с данными пользователя
    """

    username: str = Field(..., description="Имя пользователя")
    email: str = Field(..., description="Email пользователя")
    full_name: str | None = Field(None, description="Полное имя")
    role: UserRole = Field(..., description="Роль пользователя")
    is_active: bool = Field(..., description="Флаг активности")

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseResponse):
    """
    Схема ответа со списком пользователей (без чувствительных данных)
    """

    username: str
    email: str
    full_name: str | None
    role: UserRole
    is_active: bool


class UserSelfUpdate(BaseModel):
    """
    Схема для обновления своих данных (пользователем)
    """

    email: EmailStr | None = None
    full_name: str | None = Field(None, max_length=100)
