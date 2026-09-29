from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Float
from sqlalchemy.orm import relationship
from database.session import Base

class Apartamento(Base):
    __tablename__ = "apartamentos"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True, nullable=False)
    
    visitantes = relationship("Visitante", back_populates="apartamento")
    reservas = relationship("Reserva", back_populates="apartamento")

class Area(Base):
    __tablename__ = "areas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    taxa = Column(Float, default=0.0, nullable=False)
    
    reservas = relationship("Reserva", back_populates="area")

class Visitante(Base):
    __tablename__ = "visitantes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    documento = Column(String, nullable=False, unique=True)
    apartamento_id = Column(Integer, ForeignKey("apartamentos.id"), nullable=False)
    
    apartamento = relationship("Apartamento", back_populates="visitantes")

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    apartamento_id = Column(Integer, ForeignKey("apartamentos.id"), nullable=False)
    data = Column(String, nullable=False)  # Formato AAAA-MM-DD
    
    area = relationship("Area", back_populates="reservas")
    apartamento = relationship("Apartamento", back_populates="reservas")
    
    # GARANTIA 5: Constraint que impossibilita no nível do banco de dados 
    # que existam duas reservas para a mesma área na mesma data.
    __table_args__ = (
        UniqueConstraint('area_id', 'data', name='uix_reserva_area_data'),
    )
