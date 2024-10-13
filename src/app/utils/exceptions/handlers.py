from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.app.utils.exceptions.http_exceptions import CustomValidationException


async def validation_exception_handler(
        request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handles ValidationError, translating it into flat dict error data:
        * code - unique code of the error in the system
        * detail - general description of the error
        * fields - list of dicts with description of the error in each field

    :param request: Starlette Request instance
    :param exc: StarletteHTTPException instance
    :return: UJSONResponse with newly formatted error data
    """
    status_code = getattr(exc, "status_code", 400)
    errors = exc.errors()
    try:
        for error in errors:
            if error.get('loc') and isinstance(error.get('loc'), tuple):
                error['field'] = error.get('loc')[1]
                error.pop('loc', None)
        return JSONResponse(
            status_code=status_code,
            content={"detail": jsonable_encoder(errors)}
        )
    except Exception:
        return JSONResponse(
            status_code=status_code,
            content={"detail": jsonable_encoder(errors)}
        )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Helper function to setup exception handlers for app.
    Use during app startup as follows:

    .. code-block:: python

        app = FastAPI()

        @app.on_event('startup')
        async def startup():
            setup_exception_handlers(app)

    :param app: app object, instance of FastAPI
    :return: None
    """
    app.add_exception_handler(
        CustomValidationException, validation_exception_handler
    )
    app.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )
