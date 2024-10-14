from .app.api import router
from .app.core.settings import settings
from .app.core.setup import ApplicationFactory, babel  # noqa: F401

app = ApplicationFactory(router=router, settings=settings).init()
