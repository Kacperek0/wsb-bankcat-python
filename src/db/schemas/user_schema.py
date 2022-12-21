import pydantic


class _UserBase(pydantic.BaseModel):
    email: str
    name: str
    surname: str


class UserCreate(_UserBase):
    hashed_password: str

    class Config:
        orm_mode = True


class User(_UserBase):
    id: int

    class Config:
        orm_mode = True
