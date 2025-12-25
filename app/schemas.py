from pydantic import BaseModel, field_validator


class CreateUser(BaseModel):
    username: str
    email: str
    password: str


class CreateOrder(BaseModel):
    items: dict
    total_price:float
