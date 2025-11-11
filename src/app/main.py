from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.configs import settings
from app.api.v1.api import router

app = FastAPI(title="Multimeios API",
              version="1.0"
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Multimeios API!"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix=settings.API_V1_STR)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, log_level="info" ,reload=True) 