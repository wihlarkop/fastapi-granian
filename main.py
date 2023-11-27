from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from granian import Granian
from granian.constants import Interfaces
from sqlalchemy import create_engine, Engine, MetaData, URL

from config import settings

connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    database=settings.POSTGRES_DB
)


class Client:
    def __init__(self):
        self.connection_url: URL = connection_url
        self.engine: Engine = create_engine(url=self.connection_url, pool_pre_ping=True)
        self.metadata = MetaData()

    def get_engine(self) -> Engine:
        return self.engine

    def disconnect(self):
        self.engine.dispose()


client = Client()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_client = client.get_engine()
    with db_client.connect() as connection:
        yield {
            "db": connection
        }
    client.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)


@app.get("/health")
async def health(request: Request):
    return JSONResponse(content={"health": True})


if __name__ == "__main__":
    Granian(
        target="main:app",
        interface=Interfaces.ASGI,
        reload=True,
        log_enabled=True
    ).serve()
