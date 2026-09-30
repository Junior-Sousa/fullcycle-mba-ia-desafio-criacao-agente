from google.adk import Agent
from src.agents.reserva_agent import reserva_specialist
from src.agents.visitante_agent import visitante_specialist
from src.agents.sindico_agent import sindico_specialist

main_agent = Agent(
    name="assistente_aurora",
    model="gemini-2.5-flash",
    instruction="""Você é o assistente principal do condomínio Residencial Aurora.
Sua função é triar os pedidos do morador.
1. Agendamento/Listagem/Cancelamento de Áreas -> DELEGUE para reserva_specialist
2. Autorização de Visitantes -> DELEGUE para visitante_specialist
3. Dúvidas do regulamento interno -> DELEGUE para sindico_specialist

Se o morador disser que "já confirmou" ou perguntar sobre taxas, os especialistas lidarão com isso e a API cuidará do fluxo, aja com cortesia.
Lembre-se: O modelo decide o caminho, a triagem e o roteamento de delegação, mas as regras são do código.
""",
    tools=[],
    sub_agents=[reserva_specialist, visitante_specialist, sindico_specialist]
)
root_agent = main_agent
