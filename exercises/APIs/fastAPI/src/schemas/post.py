from pydantic import BaseModel
from datetime import datetime, UTC

class PostIn(BaseModel):
    title: str
    content: str
    publication_date: datetime = datetime.now(UTC)
    active: bool = True