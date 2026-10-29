from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=1, max_length=30)
    address: str = Field(min_length=1, max_length=500)

    @field_validator("password")
    @classmethod
    def password_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("비밀번호는 UTF-8 기준 72바이트 이하여야 합니다.")
        return value

    @field_validator("name", "phone", "address")
    @classmethod
    def nonblank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("공백만 입력할 수 없습니다.")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)

    @field_validator("password")
    @classmethod
    def password_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("비밀번호는 UTF-8 기준 72바이트 이하여야 합니다.")
        return value


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    phone: str
    address: str


class MessageResponse(BaseModel):
    message: str
