import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from src.database.session import Base

def generate_reserva_code():
    return f"RSV-{str(uuid.uuid4().int)[:4]}"

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String, unique=True, nullable=False, default=generate_reserva_code)
    apartamento = Column(String, ForeignKey("apartamentos.numero"), nullable=False)
    area = Column(String, ForeignKey("areas.id"), nullable=False)
    data = Column(String, nullable=False)  # Formato AAAA-MM-DD

    # GARANTIA 5: Cada área comum aceita no máximo uma reserva por data.
    __table_args__ = (
        UniqueConstraint('area', 'data', name='uix_reserva_area_data'),
    )
