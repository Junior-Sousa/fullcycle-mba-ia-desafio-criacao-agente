from google.adk import Agent
from src.tools.visitante_tools import autorizar_visitante, listar_meus_visitantes

visitante_specialist = Agent(
    name="visitante_specialist",
    model="gemini-2.5-flash",
    description="Especialista responsável por consultar e autorizar a entrada de visitantes na portaria.",
    instruction="""Você é o especialista de Visitantes da Portaria do Residencial Aurora.
Sua função é gerenciar a autorização e a consulta de visitantes do morador.
Se o usuário pedir para consultar ou listar os visitantes, use a tool `listar_meus_visitantes`.
Se o usuário pedir para autorizar um visitante, chame a tool `autorizar_visitante` passando o nome e a data.
Lembre-se: não exija nem pergunte o número do apartamento para a tool, o ID da sessão autenticada é usado implicitamente no código.
""",
    tools=[autorizar_visitante, listar_meus_visitantes]
)

