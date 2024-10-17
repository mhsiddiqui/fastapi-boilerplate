from fastcrud.exceptions.http_exceptions import NotFoundException

from core.settings import settings


class UtilMethods:
    @staticmethod
    async def get_object_or_raise_404(db, crud, schema=None, title="object", **kwargs):
        filters = {**kwargs}
        if schema:
            filters["schema_to_select"] = schema
        db_object = await crud.get(db=db, **filters)
        if db_object is None:
            raise NotFoundException(f"{title} not found")
        return db_object

    @staticmethod
    def get_absolute_url(path):
        if path:
            parsed_path = path.replace(settings.MEDIA_ROOT, "")
            return f"{settings.SERVER_URL}{settings.MEDIA_URL}{parsed_path}"
        return path
