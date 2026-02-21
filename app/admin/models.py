from sqlalchemy import Column, Integer, String
from app.store.database.database import BaseModel 

class AdminModel(BaseModel):
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True, index=True)  
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)