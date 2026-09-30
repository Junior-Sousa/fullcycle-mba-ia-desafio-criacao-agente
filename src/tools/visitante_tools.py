from google.adk.tools.tool_context import ToolContext
from src.repositories.visitante_repository import VisitanteRepository

def autorizar_visitante(nome: str, data: str, tool_context: ToolContext) -> str:
    """
    Autoriza a entrada de um novo visitante.
    Requer o nome do visitante e a data da visita no formato AAAA-MM-DD.
    """
    apartamento_id = str(tool_context.session.user_id)
    
    if tool_context.tool_confirmation is not None:
        if not tool_context.tool_confirmation.confirmed:
            return "Operação cancelada: O morador não aprovou a liberação."
    else:
        tool_context.request_confirmation(
            hint="Deseja confirmar a liberação do visitante?",
            payload={"nome": nome, "data": data}
        )
        return ""

    try:
        VisitanteRepository.criar_visitante(apartamento_id, nome, data)
        return f"Sucesso: Visitante '{nome}' autorizado para o dia {data}!"
    except Exception as e:
        return f"Erro interno ao autorizar visitante: {str(e)}"


