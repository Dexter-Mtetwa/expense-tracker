from fastapi import FastAPI,APIRouter
from contextlib import asynccontextmanager

from app.routers.expenses import router as expenses_router
from app.routers.categories import router as categories_router
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router

from app.db.database import create_pool


# Lifespan event to manage the database connection pool
@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = create_pool()
    pool.open(wait=True)

    app.state.db_pool = pool

    try:
        yield
    finally:
        pool.close()


app = FastAPI(
    title="Expense Tracker API",
    lifespan=lifespan,
)



# API Router
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(expenses_router)
api_router.include_router(categories_router)
api_router.include_router(users_router)
api_router.include_router(auth_router)


@app.get('/')
def root():
    return {'message': 'Expense Tracker API'}


@app.get('/health')
def health_check():
    return {'status': 'ok'}


app.include_router(api_router)