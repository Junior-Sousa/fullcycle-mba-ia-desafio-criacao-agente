import pytest
from agents.bot import agent
from google.adk.agents.base_agent import BaseAgent
from google.adk.tools import BaseTool

def test_agent_initialization():
    assert isinstance(agent, BaseAgent)
    assert agent.name == "assistente_aurora"
    assert "Residencial Aurora" in agent.instruction

def test_agent_tools_configured():
    # Verify the agent has exactly 6 tools configured
    assert len(agent.tools) == 6

    tool_names = [tool.__name__ for tool in agent.tools]
    assert "listar_apartamentos" in tool_names
    assert "listar_areas_comuns" in tool_names
    assert "autorizar_visitante" in tool_names
    assert "reservar_area" in tool_names
    assert "listar_minhas_reservas" in tool_names
    assert "cancelar_reserva" in tool_names

