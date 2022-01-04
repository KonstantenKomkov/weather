from pydantic import BaseModel


class Database(BaseModel):
    engine: str
    name: str
    user: str
    password: str
    host: str
    port: str


class Yandex(BaseModel):
    login: str
    password: str
    api_key: str
    token: str
    id: str


class App(BaseModel):
    secret_key: str
    database: Database
    yandex: Yandex
