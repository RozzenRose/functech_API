from pydantic import BaseModel, field_validator


class CreateUser(BaseModel):
    username: str
    email: str
    password: str


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
