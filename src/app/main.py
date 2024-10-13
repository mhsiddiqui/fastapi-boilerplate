from .api import router
from .core.settings import settings
from .core.setup import ApplicationFactory
from fastapi_babel import Babel, BabelConfigs, _

configs = BabelConfigs(
    ROOT_DIR=str(settings.BASE_DIR / "src"),
    BABEL_DEFAULT_LOCALE="en",
    BABEL_TRANSLATION_DIRECTORY="locale",
)
babel = Babel(configs=configs)

app = ApplicationFactory(router=router, settings=settings).init()
