from fastapi import APIRouter

from app.api.v1.endpoints.user import router as userRouter
from app.api.v1.endpoints.genre import router as genreRouter

router = APIRouter()

router.include_router(userRouter, prefix="/users", tags=["Usuários"])
router.include_router(genreRouter, prefix="/genres", tags=["Gêneros"])
