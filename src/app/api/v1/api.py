from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as authRouter
from app.api.v1.endpoints.user import router as userRouter

router = APIRouter()

router.include_router(authRouter, prefix="/auth", tags=["Autenticação"])
router.include_router(userRouter, prefix="/users", tags=["Usuários"])

