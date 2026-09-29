from database.session import SessionLocal
from database.models import Apartamento, Area, Visitante, Reserva
from sqlalchemy.exc import IntegrityError
from google.adk.tools.tool_context import ToolContext
def listar_apartamentos() -> list[dict]:
    """Lista todos os apartamentos disponíveis no condomínio para consulta de IDs."""
    db = SessionLocal()
    try:
        aptos = db.query(Apartamento).all()
        return [{"id": a.id, "numero": a.numero} for a in aptos]
    finally:
        db.close()

def listar_areas_comuns() -> list[dict]:
    """Lista todas as áreas comuns disponíveis para reserva e seus respectivos IDs."""
    db = SessionLocal()
    try:
        areas = db.query(Area).all()
        return [{"id": a.id, "nome": a.nome, "taxa": a.taxa} for a in areas]
    finally:
        db.close()

def autorizar_visitante(apartamento_id: int, nome: str, documento: str) -> str:
    """
    Autoriza a entrada de um novo visitante para um apartamento.
    Deve receber o ID do apartamento (inteiro), o nome e o documento do visitante.
    """
    db = SessionLocal()
    try:
        # GARANTIA 2: Trava a nível de código limitando a 3 visitantes no total
        total_visitantes = db.query(Visitante).filter(Visitante.apartamento_id == apartamento_id).count()
        if total_visitantes >= 3:
            return "Erro: Limite atingido. Um apartamento só pode receber no máximo 3 visitantes."
            
        novo_visitante = Visitante(nome=nome, documento=documento, apartamento_id=apartamento_id)
        db.add(novo_visitante)
        db.commit()
        return f"Sucesso: Visitante '{nome}' autorizado!"
    except IntegrityError:
        db.rollback()
        return "Erro: Já existe um visitante com este documento cadastrado."
    except Exception as e:
        db.rollback()
        return f"Erro interno ao autorizar visitante: {str(e)}"
    finally:
        db.close()

def reservar_area(apartamento_id: int, area_id: int, data: str, tool_context: ToolContext) -> str:
    """
    Reserva uma área comum para um apartamento.
    Requer o ID do apartamento, o ID da área, e a data no formato AAAA-MM-DD.
    """
    db = SessionLocal()
    try:
        area = db.query(Area).filter(Area.id == area_id).first()
        if not area:
            return "Erro: Área não encontrada."
            
        # GARANTIA 3: Reservar uma área com taxa maior que zero gera cobrança. Área com taxa zero não gera.
        # Exige confirmação de um ser humano via Human in the loop.
        if area.taxa > 0:
            if not tool_context.tool_confirmation or not tool_context.tool_confirmation.confirmed:
                tool_context.request_confirmation(
                    hint=f"Confirmar reserva da área {area.nome} que possui uma taxa de R$ {area.taxa:.2f}?"
                )
                return "Aguardando confirmação do usuário."

        nova_reserva = Reserva(apartamento_id=apartamento_id, area_id=area_id, data=data)
        db.add(nova_reserva)
        db.commit()
        return "Sucesso: Reserva confirmada!"
    except IntegrityError:
        db.rollback()
        # GARANTIA 5: Constraint única do banco barrando dupla-reserva no mesmo dia
        return "Erro: Esta área já está reservada por outro morador nesta data."
    except Exception as e:
        db.rollback()
        return f"Erro interno ao realizar reserva: {str(e)}"
    finally:
        db.close()

def listar_minhas_reservas(tool_context: ToolContext) -> list[dict]:
    """Lista as reservas do morador atual (sessão)."""
    db = SessionLocal()
    try:
        user_numero = tool_context.session.user_id
        apto = db.query(Apartamento).filter(Apartamento.numero == user_numero).first()
        if not apto:
            return []
        reservas = db.query(Reserva).filter(Reserva.apartamento_id == apto.id).all()
        return [{"id": r.id, "area_id": r.area_id, "data": r.data} for r in reservas]
    finally:
        db.close()

def cancelar_reserva(reserva_id: int, tool_context: ToolContext) -> str:
    """
    Cancela uma reserva existente do morador atual pelo ID da reserva.
    """
    db = SessionLocal()
    try:
        reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if not reserva:
            return "Erro: Reserva não encontrada."
        
        # GARANTIA 4: O morador só pode cancelar a própria reserva
        apartamento = db.query(Apartamento).filter(Apartamento.id == reserva.apartamento_id).first()
        if not apartamento or apartamento.numero != tool_context.session.user_id:
            return "Erro: Falha de segurança. Você não tem permissão para cancelar uma reserva de outro apartamento."
            
        db.delete(reserva)
        db.commit()
        return "Sucesso: Reserva cancelada!"
    finally:
        db.close()
