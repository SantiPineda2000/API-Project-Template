from fastapi import APIRouter
from src.users.router import user_routes, roles_routes # Users route
from src.auth.router import auth_routes # Authentication route

api_router = APIRouter()

# Add router paths here
api_router.include_router(user_routes, prefix="/users", tags=["Users CRUD"])
api_router.include_router(roles_routes, prefix="/roles", tags=["Roles CRUD"])
api_router.include_router(auth_routes, prefix="/login", tags=["OAuth2 token login"])