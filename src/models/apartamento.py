from sqlalchemy import Column, String
from src.database.session import Base

class Apartamento(Base):
    __tablename__ = "apartamentos"
    # O JSON usa "numero": "101" como identificador principal
    numero = Column(String, primary_key=True, index=True)
    morador = Column(String, nullable=False)
