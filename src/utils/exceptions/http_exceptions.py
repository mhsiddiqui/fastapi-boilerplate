# ruff: noqa
from fastapi.exceptions import ValidationException
from fastcrud.exceptions.http_exceptions import (
    CustomException,
    BadRequestException,
    NotFoundException,
    ForbiddenException,
    UnauthorizedException,
    UnprocessableEntityException,
    DuplicateValueException,
    RateLimitException,
)


class CustomValidationException(ValidationException):
    def __init__(self, message, input='', field='no-field', error_type='validation', **kwargs):
        self.msg = message
        self.input = input
        self.field = field
        self.error_type = error_type
        self.kwargs = kwargs
        self._errors = [self.json()]

    def json(self):
        return {
            'field': self.field,
            'msg': self.msg, 'input': self.input,
            'type': self.error_type, **self.kwargs
        }
