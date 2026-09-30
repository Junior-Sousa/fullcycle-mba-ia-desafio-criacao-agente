from sqlalchemy import Column, String, Float
from src.database.session import Base

class Area(Base):
    __tablename__ = "areas"
    # O JSON usa "id": "salao-de-festas"
    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    taxa = Column(Float, default=0.0)
