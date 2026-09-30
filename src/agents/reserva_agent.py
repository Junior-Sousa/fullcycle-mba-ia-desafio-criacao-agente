from google.adk import Agent
from src.tools.reserva_tools import (
    listar_areas_comuns,
    reservar_area,
    listar_minhas_reservas,
    cancelar_reserva
)

reserva_specialist = Agent(
    name="reserva_specialist",
    model="gemini-2.5-flash",
    description="Especialista responsável por agendamento, consulta e cancelamento de reservas das áreas comuns.",
    instruction="""Você é o especialista de Reservas do Residencial Aurora.
Sua função é gerenciar as solicitações relacionadas a agendamentos, consultas de reservas, e cancelamentos das áreas comuns do condomínio.
Se o usuário pedir para reservar, use a tool `reservar_area`. Você nunca pergunta qual é o apartamento do usuário, pois o sistema lida com isso.
Ao listar as áreas, use a tool `listar_areas_comuns`.
""",
    tools=[listar_areas_comuns, reservar_area, listar_minhas_reservas, cancelar_reserva]
)
