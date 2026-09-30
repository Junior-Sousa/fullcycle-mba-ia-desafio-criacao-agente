from src.database.session import SessionLocal
from src.models import Reserva
from sqlalchemy.exc import IntegrityError

class ReservaRepository:
    @staticmethod
    def criar_reserva(apartamento_id: str, area_id: str, data: str):
        db = SessionLocal()
        try:
            nova_reserva = Reserva(apartamento=apartamento_id, area=area_id, data=data)
            db.add(nova_reserva)
            db.commit()
            return nova_reserva
        except IntegrityError:
            db.rollback()
            raise ValueError("Erro: Esta área já está reservada por outro morador nesta data.")
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def listar_reservas_por_apartamento(apartamento_id: str):
        db = SessionLocal()
        try:
            return db.query(Reserva).filter(Reserva.apartamento == apartamento_id).all()
        finally:
            db.close()

    @staticmethod
    def obter_reserva(codigo: str):
        db = SessionLocal()
        try:
            return db.query(Reserva).filter(Reserva.codigo == codigo).first()
        finally:
            db.close()

    @staticmethod
    def excluir_reserva(reserva: Reserva):
        db = SessionLocal()
        try:
            r = db.query(Reserva).filter(Reserva.codigo == reserva.codigo).first()
            if r:
                db.delete(r)
                db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
