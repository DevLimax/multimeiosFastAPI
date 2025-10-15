from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as authRouter
from app.api.v1.endpoints.user import router as userRouter
from app.api.v1.endpoints.genre import router as genreRouter
from app.api.v1.endpoints.book import router as bookRouter
from app.api.v1.endpoints.reviews import router as reviewRouter
from app.api.v1.endpoints.requestLoan import router as requestLoanRouter

router = APIRouter()

router.include_router(authRouter, prefix="/auth", tags=["Autenticação"])
router.include_router(userRouter, prefix="/users", tags=["Usuários"])
router.include_router(genreRouter, prefix="/genres", tags=["Gêneros"])
router.include_router(bookRouter, prefix="/books", tags=["Livros"])
router.include_router(reviewRouter, prefix="/reviews", tags=["Avaliações"])
router.include_router(requestLoanRouter, prefix="/requests", tags=["Solicitações"])

