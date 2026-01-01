from pydantic import BaseModel
from datetime import datetime, UTC


class PostOut(BaseModel):
    title: str
    content: str
    publication_date: datetime = datetime.now(UTC)