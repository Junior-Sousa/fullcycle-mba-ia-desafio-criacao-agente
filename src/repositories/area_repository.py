from src.database.session import SessionLocal
from src.models import Area

class AreaRepository:
    @staticmethod
    def listar_areas():
        db = SessionLocal()
        try:
            return db.query(Area).all()
        finally:
            db.close()

    @staticmethod
    def obter_area(area_id: str):
        db = SessionLocal()
        try:
            return db.query(Area).filter(Area.id == area_id).first()
        finally:
            db.close()
