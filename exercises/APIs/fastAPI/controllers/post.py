from typing_extensions import Annotated
from fastapi import status, Cookie, Response, Header, APIRouter
from datetime import datetime, UTC
from pydantic import BaseModel
from schemas.post import PostIn
from views.post import PostOut
import typing

router = APIRouter(prefix="/posts")



class Foo(BaseModel):
    bar: str
    message: str


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostOut)
def create_post(post: PostIn):
    return {"message": "Post created", "post": post}


@router.get("/", response_model=list[PostOut])
def read_posts(response: Response, limit: int, ads_id: Annotated[str | None, Cookie()] = None, skip: int = 0, active: bool = True, user_agent: Annotated[typing.Optional[str], Header()] = None):
    response.set_cookie(key="user", value="test_cookie_value")
    print(f"ads_id: {ads_id}")
    print(f"User-Agent: {user_agent}")
    return []
