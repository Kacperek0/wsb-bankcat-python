import pydantic
from fastapi import Query


class _UserBase(pydantic.BaseModel):
    email: pydantic.EmailStr
    name: str = Query(..., min_length=3, max_length=255)
    surname: str = Query(..., min_length=3, max_length=255)


class UserCreate(_UserBase):
    hashed_password: str = Query(..., min_length=8, max_length=255, regex=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$")

    class Config:
        orm_mode = True


class User(_UserBase):
    id: int

    class Config:
        orm_mode = True
