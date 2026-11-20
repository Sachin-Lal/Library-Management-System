from contextlib import asynccontextmanager

from fastapi import FastAPI

from .excel_handler import initialize_workbook
from .routes import auth, books, borrowing, fines, members


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_workbook()
    yield


app = FastAPI(title="Library Management System", version="1.0.0", lifespan=lifespan)


@app.get("/")
def root() -> dict:
    return {"message": "Library Management System API"}


app.include_router(auth.router)
app.include_router(members.router)
app.include_router(books.router)
app.include_router(borrowing.router)
app.include_router(fines.router)
