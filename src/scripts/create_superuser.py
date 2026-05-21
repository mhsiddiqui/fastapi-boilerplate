import re

import click
from cmd_manager import Argument, BaseCommand
from pydantic import EmailStr, ValidationError
from pydantic_core import PydanticCustomError
from sqlalchemy import or_, select

from src.core.security import hash_password
from src.models.user import User


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = self.kwargs.get("db")

    def get_arguments(self) -> list[Argument]:
        def validate_email(ctx, param, value):
            try:
                return EmailStr._validate(value)
            except (ValidationError, PydanticCustomError) as exc:
                raise click.BadParameter(f"Invalid email address: {value}") from exc

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

    def _user_exists(self, email: str, username: str) -> bool:
        stmt = select(User.id).where(or_(User.email == email, User.username == username)).limit(1)
        return self.db.execute(stmt).first() is not None

    def run(self, *args, **kwargs):
        email = kwargs["email"].lower()
        username = kwargs["username"].lower()
        if self._user_exists(email, username):
            click.echo("User already exists")
            return

        user = User(
            name=kwargs["name"],
            username=username,
            email=email,
            password=hash_password(kwargs["password"]),
            is_active=True,
            is_superuser=True,
        )
        self.db.add(user)
        self.db.commit()
        click.echo("User created successfully")
