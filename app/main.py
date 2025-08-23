from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.db import create_db, close_engine
from app.routes.auth_routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # pylint: disable= redefined-outer-name
    await create_db()
    yield
    await close_engine()


app = FastAPI(title="Authorization Service", lifespan=lifespan)

app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Auth Service is running"}
