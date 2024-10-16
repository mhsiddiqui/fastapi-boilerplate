from core.setup import ApplicationFactory
from core.settings import settings

app = ApplicationFactory(settings=settings).init()