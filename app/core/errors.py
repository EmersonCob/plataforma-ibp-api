import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "app_error") -> None:
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "code": exc.code},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "Não foi possível concluir a solicitação."
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": detail},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        logger.info("Request validation failed")
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Confira os dados informados e tente novamente.",
                "code": "validation_error",
            },
        )

    @app.exception_handler(ResponseValidationError)
    async def response_validation_error_handler(request: Request, exc: ResponseValidationError) -> JSONResponse:
        logger.exception("Response validation failed on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Não foi possível concluir a solicitação agora. Tente novamente em instantes.",
                "code": "internal_response_error",
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(_: Request, exc: ValidationError) -> JSONResponse:
        logger.info("Application validation failed")
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Confira os dados informados e tente novamente.",
                "code": "validation_error",
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Não foi possível concluir a solicitação agora. Tente novamente em instantes.",
                "code": "internal_error",
            },
        )


def not_found(message: str = "Recurso não encontrado") -> HTTPException:
    return HTTPException(status_code=404, detail=message)
