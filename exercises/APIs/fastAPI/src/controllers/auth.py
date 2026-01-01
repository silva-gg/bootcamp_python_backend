from fastapi import APIRouter
from security import sign_jwt
from schemas.auth import LoginIn
from views.auth import LoginOut

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=LoginOut)
async def login(user: LoginIn):
    token = sign_jwt(user.username)
    return token
