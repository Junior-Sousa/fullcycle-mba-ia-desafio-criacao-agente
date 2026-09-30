from src.database.session import SessionLocal
from src.models import Visitante

class VisitanteRepository:
    @staticmethod
    def criar_visitante(apartamento_id: str, nome: str, data: str):
        db = SessionLocal()
        try:
            novo_visitante = Visitante(nome=nome, data=data, apartamento=apartamento_id)
            db.add(novo_visitante)
            db.commit()
            return novo_visitante
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def listar_visitantes_por_apartamento(apartamento_id: str):
        db = SessionLocal()
        try:
            return db.query(Visitante).filter(Visitante.apartamento == apartamento_id).all()
        finally:
            db.close()
