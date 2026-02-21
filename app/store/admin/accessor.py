from typing import TYPE_CHECKING, Optional

from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError

from app.admin.models import AdminModel
from app.base.base_accessor import BaseAccessor
from app.admin.utils import hash_password

if TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        self.app = app
        await self.create_admin(
            email=self.app.config.admin.email,
            password=hash_password(self.app.config.admin.password)
        )

    async def get_by_email(self, email: str) -> Optional[AdminModel]:
        query = select(AdminModel).where(AdminModel.email == email)
        async with self.app.database.session() as session:
            result = await session.execute(query)
            admin = result.scalar_one_or_none()
            
        if admin:
            return admin
            
        if self.app.config.admin.email == email:
            return AdminModel(
                id=1,  
                email=self.app.config.admin.email,
                password=(self.app.config.admin.password)
            )
        
        return None
    
    async def get_by_id(self, id: int) -> Optional[AdminModel]:
        query = select(AdminModel).where(AdminModel.id == id)
        async with self.app.database.session() as session:
            result = await session.execute(query)
            admin = result.scalar_one_or_none()
            
        if admin:
            return admin
            
        if self.app.config.admin.id == id:
            return AdminModel(
                id=1,  
                email=self.app.config.admin.email,
                password=(self.app.config.admin.password)
            )
        
        return None

    async def create_admin(self, email: str, password: str) -> Optional[AdminModel]:
        hashed_password = hash_password(password)
        
        query = insert(AdminModel).values(
            email=email,
            password=hashed_password
        ).returning(AdminModel)
        
        async with self.app.database.session() as session:
            try:
                result = await session.execute(query)
                await session.commit()
                return result.scalar_one()
            except IntegrityError:
                await session.rollback()
                return None