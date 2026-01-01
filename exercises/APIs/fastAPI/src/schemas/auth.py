from pydantic import BaseModel

class LoginIn(BaseModel):
    username: str