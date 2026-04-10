from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    username: str
    email: str
    password: str
    role: str
    showroom_id: int | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    role: str
    showroom_name: str | None = None

    class Config:
        from_attributes = True


class PasswordUpdate(BaseModel):
    password: str