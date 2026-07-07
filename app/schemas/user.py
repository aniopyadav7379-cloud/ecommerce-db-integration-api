from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserProfileBase(BaseModel):
    phone_number: str | None = Field(default=None, max_length=20)
    address_line: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileRead(UserProfileBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=150)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    profile: UserProfileCreate | None = None


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserRead(UserBase):
    id: int
    profile: UserProfileRead | None = None
    model_config = ConfigDict(from_attributes=True)
