from pydantic import BaseModel
from datetime import datetime, UTC

class PostIn(BaseModel):
    title: str
    date: datetime = datetime.now(UTC)
    active: bool = True