from pydantic import BaseModel, Field, field_validator


class ProfileUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=1, max_length=30)
    address: str = Field(min_length=1, max_length=500)

    @field_validator("name", "phone", "address")
    @classmethod
    def nonblank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("공백만 입력할 수 없습니다.")
        return value


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8)

    @field_validator("current_password", "new_password")
    @classmethod
    def password_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("비밀번호는 UTF-8 기준 72바이트 이하여야 합니다.")
        return value


class AccountDelete(BaseModel):
    password: str = Field(min_length=1)

    @field_validator("password")
    @classmethod
    def password_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("비밀번호는 UTF-8 기준 72바이트 이하여야 합니다.")
        return value
