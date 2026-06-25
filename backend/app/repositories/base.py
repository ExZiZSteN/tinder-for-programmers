from typing import Generic, Sequence, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base


ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    '''
    Универасальный CRUD-репозиторий.

    Наследники будут получать операции из коробки
    и могут переопределять их или расширять
    '''

    def __init__(self, model: type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get(self, id: int) -> ModelType | None:
        return await self.db.get(self.model, id)
    
    async def get_or_404(self, id: int) -> ModelType:
        isinstance = await self.get(id)
        if isinstance is None:
            from app.core.exceptions import NotFoundException
            raise NotFoundException(self.model.__name__)
        return isinstance
    
    async def get_all(self, *, limit: int = 100, offset: int = 0,) -> Sequence[ModelType]:
        query = (select(self.model).limit(limit).offset(offset))
        result = await self.db.execute(query)
        return result.scalar().all()
    
    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def update(self, instance: ModelType, **kwargs) -> ModelType:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self.db.delete(instance)
        await self.db.flush()

    async def save(self, instance: ModelType) -> ModelType:
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance