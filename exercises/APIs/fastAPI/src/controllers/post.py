from typing_extensions import Annotated
from fastapi import status, Cookie, Response, Header, APIRouter
from schemas.post import PostIn
from views.post import PostOut
from security import login_required
from fastapi import Depends
from models.post import posts
from database import database
import typing

router = APIRouter(prefix="/posts", dependencies=[Depends(login_required)])

@router.get("/", response_model=list[PostOut])
async def read_posts(title: str | None = None):
    try:
        query = posts.select()
        if title:
            query = query.where(posts.c.title.ilike(f"%{title}%"))
    except Exception as e:
        print(f"Error occurred: {e}")
        raise e
    return await database.fetch_all(query)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostOut)
async def create_post(post: PostIn):
    query = posts.insert().values(**post.model_dump())
    registered_post_id = await database.execute(query)
    return {**post.model_dump(), "id": registered_post_id}

@router.patch("/{post_id}", response_model=PostOut)
async def update_post(post_id: int, post: PostIn):
    query = posts.update().where(posts.c.id == post_id).values(**post.model_dump())
    await database.execute(query)
    return {**post.model_dump(), "id": post_id}

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int):
    query = posts.delete().where(posts.c.id == post_id)
    await database.execute(query)
    return Response(status_code=status.HTTP_204_NO_CONTENT)