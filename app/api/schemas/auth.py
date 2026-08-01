from pydantic import BaseModel, Field, field_validator
from app.exceptions import ValidationError


class LoginRequest(BaseModel):
    """
    Схема запроса на логин
    """

    username: str = Field(
        ..., min_length=3, max_length=50, description="Имя пользователя"
    )
    password: str = Field(..., min_length=6, max_length=100, description="Пароль")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Проверяет, что username содержит только допустимые символы."""
        if not v.isalnum() and "_" not in v:
            raise ValidationError(
                "Имя пользователя может содержать только буквы, цифры и символ подчеркивания"
            )
        return v.lower()


class TokenResponse(BaseModel):
    """
    Схема ответа с JWT токеном
    """

    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field("bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")
    user_id: int = Field(..., description="ID пользователя")
    role: str = Field(..., description="Роль пользователя")
