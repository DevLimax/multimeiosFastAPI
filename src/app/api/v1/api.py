from fastapi import APIRouter

from app.api.v1.endpoints.user import router as userRouter

router = APIRouter()

router.include_router(userRouter, prefix="/users", tags=["Usuários"])