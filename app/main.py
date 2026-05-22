from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.errors import format_validation_errors, validation_error_message
from app.api.v1 import (
    orders,
    payments,
    shipments,
    products,
    devices,
    auth,
    roles,
    users,
    internal,
)

app = FastAPI(
    title="GAC API",
    description="Backend API for Gemini Admin Console",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:3000",  # Common frontend port
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://10.8.0.1:5160",
    "http://localhost:5160",
    "http://127.0.0.1:5160",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    errors = format_validation_errors(exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "message": validation_error_message(exc.errors()),
            "data": None,
            "error": "validation_error",
            "detail": errors,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail
    message = detail if isinstance(detail, str) else str(detail)
    content: dict = {
        "message": message,
        "data": None,
        "error": f"http_{exc.status_code}",
    }
    if not isinstance(detail, str):
        content["detail"] = detail
    return JSONResponse(status_code=exc.status_code, content=content)


# Include Routers
app.include_router(orders.router, prefix="/api/v1", tags=["orders"])
app.include_router(payments.router, prefix="/api/v1", tags=["payments"])
app.include_router(shipments.router, prefix="/api/v1", tags=["shipments"])
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(devices.router, prefix="/api/v1", tags=["devices"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(roles.router, prefix="/api/v1", tags=["roles"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(internal.router, prefix="/api/v1", tags=["internal"])


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint con metadatos básicos del servicio."""
    return {
        "status": "ok",
        "service": "gac-api",
        "version": app.version,
    }
