from src.database.session import SessionLocal
from src.models import Reserva, ReservaSequencia
from src.models.reserva import generate_reserva_code
from sqlalchemy.exc import IntegrityError

class ReservaRepository:
    @staticmethod
    def gerar_proximo_codigo(db) -> str:
        seq = db.query(ReservaSequencia).filter(ReservaSequencia.id == 1).with_for_update().first()
        if not seq:
            maior = 5000
            for r in db.query(Reserva.codigo).all():
                if r.codigo and r.codigo.startswith("RSV-"):
                    num = r.codigo.replace("RSV-", "")
                    if num.isdigit() and int(num) >= maior:
                        maior = int(num) + 1
            seq = ReservaSequencia(id=1, proximo_numero=maior)
            db.add(seq)
            db.flush()

        numero = seq.proximo_numero
        seq.proximo_numero += 1
        db.flush()
        return f"RSV-{numero}"

    @staticmethod
    def criar_reserva(apartamento_id: str, area_id: str, data: str, max_retries: int = 3):
        db = SessionLocal()
        try:
            # Checagem prévia se a área já está reservada na data solicitada
            reserva_existente = db.query(Reserva).filter(Reserva.area == area_id, Reserva.data == data).first()
            if reserva_existente:
                raise ValueError("Erro: Esta área já está reservada por outro morador nesta data.")

            for tentativa in range(max_retries):
                try:
                    codigo = ReservaRepository.gerar_proximo_codigo(db)
                    nova_reserva = Reserva(
                        apartamento=apartamento_id,
                        area=area_id,
                        data=data,
                        codigo=codigo
                    )
                    db.add(nova_reserva)
                    db.commit()
                    db.refresh(nova_reserva)
                    return nova_reserva
                except IntegrityError as e:
                    db.rollback()
                    err_str = str(e).lower()

                    # Conflito de área e data (UniqueConstraint uix_reserva_area_data)
                    if "uix_reserva_area_data" in err_str or "reservas.area" in err_str or "reservas.data" in err_str:
                        raise ValueError("Erro: Esta área já está reservada por outro morador nesta data.")

                    # Colisão do código da reserva (UniqueConstraint reservas.codigo)
                    if "reservas.codigo" in err_str or "codigo" in err_str:
                        if tentativa < max_retries - 1:
                            continue
                        raise ValueError("Erro: Falha de colisão ao gerar identificador único para a reserva. Tente novamente.")

                    # Fallback de verificação caso o texto do erro da constraint seja opaco no driver
                    if db.query(Reserva).filter(Reserva.area == area_id, Reserva.data == data).first():
                        raise ValueError("Erro: Esta área já está reservada por outro morador nesta data.")

                    raise ValueError("Erro de integridade ao processar a reserva.")
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
