from fastapi import APIRouter
from app.api.endpoints import auth, users, nutrition, workouts, supplements, ai, stripe_pay, admin

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(nutrition.router)
api_router.include_router(workouts.router)
api_router.include_router(supplements.router)
api_router.include_router(ai.router)
api_router.include_router(stripe_pay.router)
api_router.include_router(admin.router)
