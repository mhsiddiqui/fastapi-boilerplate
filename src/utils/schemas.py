from pydantic import BaseModel

class BaseSchema(BaseModel):

    async def is_valid(self, crud, db) -> bool:
        all_fields = self.model_fields
        for field in all_fields:
            validation_method = getattr(self, f'validate_{field}', None)
            if validation_method:
                await validation_method(getattr(self, field), crud, db)
        await self.validate_all(crud, db)
        return True

    async def validate_all(self, crud, db):
        return True

    async def create(self, crud, db):
        pass

    async def update(self,crud, db, **kwargs):
        pass


