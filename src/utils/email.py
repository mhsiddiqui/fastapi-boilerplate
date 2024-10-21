import abc

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse

from core.settings import settings

from .render import render


class BaseBackend(abc.ABC):
    @property
    def conf(self):
        return ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_BACKEND,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=settings.USE_CREDENTIALS,
            VALIDATE_CERTS=settings.VALIDATE_CERTS,
        )

    def __init__(self, subject, recipients, template, context, subtype=MessageType.html):
        self.subject = subject
        self.recipients = recipients
        self.template = template
        self.context = context
        self.subtype = subtype

    @property
    def message(self):
        return MessageSchema(
            subject=self.subject,
            recipients=self.recipients,
            body=render(self.template, **self.context),
            subtype=MessageType.html,
        )

    @abc.abstractmethod
    async def send(self):
        pass


class FileBackend(BaseBackend):
    async def send(self, background=False):
        assert settings.MAIL_FILE_PATH, "MAIL_FILE_PATH is not set"
        pass


class SmtpBackend(BaseBackend):
    async def send(self):
        fm = FastMail(self.conf)
        await fm.send_message(self.message)
        return JSONResponse(status_code=200, content={"message": "Email has been sent"})


def send_mail(subject, recipients, template, context):
    mail_backend = settings.MAIL_BACKEND
    if mail_backend == "file":
        backend = FileBackend(subject, recipients, template, context)
    else:
        backend = SmtpBackend(subject, recipients, template, context)
    return backend.send()


class EmailUtil:
    def __init__(
        self, from_email=None, to_emails=None, subject="", text_body=None, html_template=None, template_data=None
    ):
        self.from_email = from_email or settings.MAIL_FROM
        self.to_emails = to_emails or []
        self.subject = subject
        self.text_body = text_body
        self.html_template = html_template
        self.template_data = template_data or {}

    def send(self):
        data = {
            "subject": self.subject,
            "message": self.text_body,
            "from_email": self.from_email,
            "recipient_list": self.to_emails,
        }
        if self.html_template:
            data["html_message"] = self._html_body()
        send_mail(**data)

    def _html_body(self):
        return render(template_name=self.html_template, context=self.template_data)
