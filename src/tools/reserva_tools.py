from google.adk.tools.tool_context import ToolContext
from src.repositories.area_repository import AreaRepository
from src.repositories.reserva_repository import ReservaRepository

def listar_areas_comuns() -> list[dict]:
    """Lista todas as áreas comuns disponíveis para reserva, retornando o ID da área, nome e valor da taxa."""
    areas = AreaRepository.listar_areas()
    return [{"id": a.id, "nome": a.nome, "taxa": a.taxa} for a in areas]

def reservar_area(area_id: str, data: str, tool_context: ToolContext) -> str:
    """
    Reserva uma área comum para a data solicitada.
    Requer o ID da área (obtido através da listagem de áreas) e a data no formato AAAA-MM-DD.
    """
    apartamento_id = str(tool_context.session.user_id)
    area = AreaRepository.obter_area(area_id)
    
    if not area:
        return "Erro: Área não encontrada. Use listar_areas_comuns para ver as áreas disponíveis."
        
    if area.taxa > 0:
        if tool_context.tool_confirmation is not None:
            if not tool_context.tool_confirmation.confirmed:
                return "Operação cancelada: O morador não aprovou a taxa."
        else:
            tool_context.request_confirmation(
                hint=f"Confirmar reserva da área '{area.nome}' gerando uma taxa de R$ {area.taxa:.2f}?",
                payload={"area": area_id, "data": data}
            )
            return ""
            
    try:
        ReservaRepository.criar_reserva(apartamento_id, area_id, data)
        return "Sucesso: Reserva confirmada!"
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Erro interno ao realizar reserva: {str(e)}"

def listar_minhas_reservas(tool_context: ToolContext) -> list[dict]:
    """Lista as reservas do morador logado na sessão."""
    apartamento_id = str(tool_context.session.user_id)
    reservas = ReservaRepository.listar_reservas_por_apartamento(apartamento_id)
    return [{"id": r.id, "codigo": r.codigo, "area_id": r.area, "data": r.data} for r in reservas]


def cancelar_reserva(codigo: str, tool_context: ToolContext) -> str:
    """
    Cancela uma reserva existente do morador atual informando o código da reserva (ex: RSV-1234).
    """
    apartamento_id = str(tool_context.session.user_id)
    reserva = ReservaRepository.obter_reserva(codigo)
    
    if not reserva:
        return "Erro: Reserva não encontrada."
    
    if reserva.apartamento != apartamento_id:
        return "Erro de Segurança: Você não pode cancelar uma reserva que não pertence ao seu apartamento."
        
    try:
        ReservaRepository.excluir_reserva(reserva)
        return "Sucesso: Reserva cancelada sem custos."
    except Exception as e:
        return f"Erro interno ao cancelar reserva: {str(e)}"
