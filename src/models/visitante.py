from sqlalchemy import Column, Integer, String, ForeignKey
from src.database.session import Base

class Visitante(Base):
    __tablename__ = "visitantes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    apartamento = Column(String, ForeignKey("apartamentos.numero"), nullable=False)
    nome = Column(String, nullable=False)
    data = Column(String, nullable=False)  # Formato AAAA-MM-DD
