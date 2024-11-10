# import sentry_sdk <- Uncomment after reading about the package
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.router import api_router
from src.config import settings
from src.initial_data import main as initial_data

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

if settings.SENTRY_DSN and settings.ENVIRONMENT != 'local':
    # Add sentry_sdk package to enable automatic error reporting, docs at: "https://docs.sentry.io/platforms/python/". 
    pass

# Creating initial data at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    initial_data()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan= lifespan
)

# Set all cors enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

app.include_router(api_router, prefix=settings.API_V1_STR)