from fastapi import FastAPI
from controllers import post
import sqlalchemy as sqa
import databases
from contextlib import asynccontextmanager


#msvc - model, service, view, controller
DATABASE_URL = "sqlite:///./test.db"
metadata = sqa.MetaData()
database = databases.Database(DATABASE_URL)

engine = sqa.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
app.include_router(post.router)


