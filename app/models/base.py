from sqlalchemy import Column, Integer, DateTime
from datetime import datetime
from app.core.database import Base

class BaseModel(Base):
    """Modelo base con campos comunes"""
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convierte el modelo a un diccionario"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    @classmethod
    def from_dict(cls, data):
        """Crea una instancia del modelo desde un diccionario"""
        return cls(**{
            key: value
            for key, value in data.items()
            if key in cls.__table__.columns.keys()
        })