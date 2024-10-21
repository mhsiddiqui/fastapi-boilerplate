from jinja2 import Environment, PackageLoader, select_autoescape

from core.settings.dev import settings

env = Environment(loader=PackageLoader("", package_path=settings.TEMPLATES_DIR), autoescape=select_autoescape())


def render(template_name: str, context: dict = None) -> str:
    context = context or {}
    template = env.get_template(template_name)
    return template.render(**context)
