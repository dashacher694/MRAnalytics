"""
Centralized error handler like in calendar_service
"""
from fastapi import status, Request, FastAPI
from fastapi.exceptions import RequestValidationError, StarletteHTTPException
from starlette.responses import JSONResponse

from src.core.fastapi.responses import ErrorResponse
from src.modules.utils.errors import NotFoundError, BadRequestError, ConflictError


def init_error_handler(app: FastAPI, admin_email: str):
    @app.exception_handler(Exception)
    async def internal_server_error_handle(req: Request, exc: Exception):
        content = ErrorResponse(
            title=type(exc).__name__,
            description=str(exc) + f", Contact me ({admin_email})",
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=content.model_dump()
        )

    @app.exception_handler(NotFoundError)
    async def not_found_error_handle(req: Request, exc: NotFoundError):
        content = ErrorResponse(
            title="not:found",
            description=str(exc),
        )
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=content.model_dump(),
        )

    @app.exception_handler(BadRequestError)
    async def bad_request_error_handle(req: Request, exc: BadRequestError):
        content = ErrorResponse(
            title="invalid:data",
            description=str(exc),
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=content.model_dump(),
        )

    @app.exception_handler(ConflictError)
    async def conflict_error_handle(req: Request, exc: ConflictError):
        content = ErrorResponse(
            title="conflict",
            description=str(exc),
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=content.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handle(req: Request, exc: RequestValidationError):
        content = ErrorResponse(
            title="invalid:data",
            description="wrong value",
            extra=exc.errors(),
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=content.model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handle(req: Request, exc: StarletteHTTPException):
        if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            return await internal_server_error_handle(req, exc)

        return JSONResponse(
            content=dict(message=str(exc.detail)), status_code=exc.status_code
        )
