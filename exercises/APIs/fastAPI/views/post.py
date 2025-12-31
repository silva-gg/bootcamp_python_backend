from pydantic import BaseModel
from datetime import datetime, UTC


class PostOut(BaseModel):
    title: str
    date: datetime = datetime.now(UTC)
    active: bool = True