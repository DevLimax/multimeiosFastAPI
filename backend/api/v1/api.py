from fastapi import APIRouter
from api.v1.endpoints import books, genres, requestLoans, reviews, users, loans

router = APIRouter()
router.include_router(users.router, prefix="/users", tags=["Usuários"])
router.include_router(books.router, prefix="/books", tags=["Livros"])
router.include_router(genres.router, prefix="/genres", tags=["Gêneros"])
router.include_router(reviews.router, prefix="/reviews", tags=["Avaliações"])
router.include_router(requestLoans.router, prefix="/requestsLoans", tags=["Solicitações de emprestimo"])
router.include_router(loans.router, prefix="/loans", tags=["Emprestimos"])

