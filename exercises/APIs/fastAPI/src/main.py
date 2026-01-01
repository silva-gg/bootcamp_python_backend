from fastapi import FastAPI
from controllers import post, auth
from database import database, engine, metadata
from contextlib import asynccontextmanager


#msvc - model, service, view, controller

@asynccontextmanager
async def lifespan(app: FastAPI):
    from models.post import posts # noqa
    metadata.create_all(engine)
    
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
app.include_router(auth.router)
app.include_router(post.router)


