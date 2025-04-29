from fastapi import FastAPI  # Import FastAPI to create the application
from app.api.v1 import auth  # Import the auth routes
from app.db.base import Base  # Base class for SQLAlchemy models
from app.db.session import engine  # DB engine to bind models
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)  # Create tables if not exist

app = FastAPI()  # Initialize FastAPI app

# Register routes from auth module
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

origins = [
    "http://localhost:3000",  # your Next.js dev server
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # must not use ["*"] with credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom OpenAPI schema for Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="Paste your Bearer token to authenticate",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Hook into FastAPI
app.openapi = custom_openapi
