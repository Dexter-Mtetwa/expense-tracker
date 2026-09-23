from fastapi import FastAPI,APIRouter

from app.routers.expenses import router as expenses_router
from app.routers.categories import router as categories_router
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router


app = FastAPI()
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