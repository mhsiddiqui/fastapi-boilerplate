import re

import click
from cmd_manager import Argument, BaseCommand
from pydantic import EmailStr, ValidationError
from pydantic_core import PydanticCustomError
from sqlalchemy import or_

from src.features.account.models import User
from src.utils.authentication import get_password_hash


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = self.kwargs.get("db")

    def get_arguments(self) -> list[Argument]:
        def validate_email(ctx, param, value):
            try:
                # Use Pydantic's EmailStr to validate the email
                email = EmailStr._validate(value)
                return email
            except (ValidationError, PydanticCustomError):
                # Raise a Click validation error if the email is not valid
                raise click.BadParameter(f"Invalid email address: {value}")

        def validate_password(ctx, param, value):
            pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
            if not re.match(pattern, value):
                raise click.BadParameter(
                    "Password must contain one uppercase, one lowercase, one digit and one special character"
                )
            return value

        return [
            Argument("--username", is_argument=False, required=True, prompt="Enter username"),
            Argument("--email", callback=validate_email, required=True, prompt="Enter Email"),
            Argument("--name", required=True, prompt="Enter Name"),
            Argument("--password", callback=validate_password, required=True, prompt="Enter Password"),
        ]

    def if_user_exists(self, email, username):
        if_user_exists = User.query().where(or_(User.email == email, User.username == username)).limit(1)
        result = self.db.execute(if_user_exists)
        return result.first() is not None

    def run(self, *args, **kwargs):
        if self.if_user_exists(kwargs.get("email"), kwargs.get("username")):
            click.echo("User already exists")
            return
        user = User(
            name=kwargs.get("name"),
            username=kwargs.get("username").lower(),
            email=kwargs.get("email").lower(),
            password=get_password_hash(kwargs.get("password")),
            is_active=True,
            is_superuser=True,
        )
        self.db.add(user)
        self.db.commit()
        click.echo("User created successfully")
