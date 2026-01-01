from pydantic import BaseModel

class LoginOut(BaseModel):
    token: str