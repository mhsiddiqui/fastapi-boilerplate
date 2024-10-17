from core.settings import settings
from core.setup import ApplicationFactory

app = ApplicationFactory(settings=settings).init()
