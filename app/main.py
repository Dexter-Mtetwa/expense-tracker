from fastapi import FastAPI,APIRouter
from contextlib import asynccontextmanager
import logging

from app.logging_config import configure_logging
from app.db.database import create_pool

from app.routers.expenses import router as expenses_router
from app.routers.categories import router as categories_router
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router


configure_logging()

# Get the logger for this module
logger = logging.getLogger(__name__)

# Lifespan event to manage the database connection pool
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")

    pool = create_pool()
    pool.open(wait=True)

    app.state.db_pool = pool

    try:
        yield
    finally:
        logger.info("Shutting down application")
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