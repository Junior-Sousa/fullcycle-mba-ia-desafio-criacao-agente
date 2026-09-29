import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import sys
from pathlib import Path
from unittest.mock import patch

# Injeta a raiz do projeto no path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.models import Base, Apartamento, Area, Visitante, Reserva
import tools.functions

# -------------------------------------------------------------------
# Configuração de Banco de Dados Em Memória para os Testes
# -------------------------------------------------------------------
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Cria as tabelas do zero para cada teste
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Massa de dados básica para os testes
    apto = Apartamento(id=1, numero="101")
    area = Area(id=1, nome="Churrasqueira")
    session.add(apto)
    session.add(area)
    session.commit()
    
    yield session
    
    session.close()
    # Apaga as tabelas após o teste para manter o isolamento
    Base.metadata.drop_all(bind=engine)


# -------------------------------------------------------------------
# Testes do Nível de Banco de Dados (Models)
# -------------------------------------------------------------------

def test_modelo_garantia_5_dupla_reserva(db_session):
    """Testa se o SQLite realmente proíbe duas reservas para a mesma área e data"""
    reserva1 = Reserva(apartamento_id=1, area_id=1, data="2024-12-25")
    db_session.add(reserva1)
    db_session.commit()
    
    reserva2 = Reserva(apartamento_id=1, area_id=1, data="2024-12-25")
    db_session.add(reserva2)
    
    # O banco DEVE gerar um IntegrityError devido ao UniqueConstraint
    with pytest.raises(IntegrityError):
        db_session.commit()


# -------------------------------------------------------------------
# Testes das Funções (Tools do Agente)
# -------------------------------------------------------------------

class MockSession:
    def __init__(self, user_id):
        self.user_id = user_id

class MockToolConfirmation:
    def __init__(self, confirmed=False):
        self.confirmed = confirmed

class MockToolContext:
    def __init__(self, user_id="101", confirmed=False):
        self.session = MockSession(user_id)
        self.tool_confirmation = MockToolConfirmation(confirmed)
        self.requested_hint = None

    def request_confirmation(self, hint):
        self.requested_hint = hint

def test_funcao_reservar_area_sucesso(db_session):
    """Testa o caminho feliz de uma reserva sem taxa"""
    with patch("tools.functions.SessionLocal", return_value=db_session):
        ctx = MockToolContext()
        msg = tools.functions.reservar_area(apartamento_id=1, area_id=1, data="2024-12-24", tool_context=ctx)
        assert "Sucesso" in msg

def test_funcao_reservar_area_falha_dupla(db_session):
    """Testa o fluxo da Garantia 5 pela visão da Função (Agente)"""
    with patch("tools.functions.SessionLocal", return_value=db_session):
        ctx = MockToolContext()
        # Primeira reserva (sucesso)
        tools.functions.reservar_area(apartamento_id=1, area_id=1, data="2024-12-25", tool_context=ctx)
        
        # Segunda reserva no mesmo dia (deve ser engolida e retornar texto amigável)
        msg = tools.functions.reservar_area(apartamento_id=1, area_id=1, data="2024-12-25", tool_context=ctx)
        
        assert "Erro" in msg
        assert "já está reservada" in msg

def test_funcao_reservar_area_com_taxa(db_session):
    """Testa o fluxo da Garantia 3 (Confirmação para áreas pagas)"""
    with patch("tools.functions.SessionLocal", return_value=db_session):
        # Area 2 tem taxa 100
        area = Area(id=2, nome="Salão", taxa=100.0)
        db_session.add(area)
        db_session.commit()
        
        ctx_unconfirmed = MockToolContext(confirmed=False)
        msg = tools.functions.reservar_area(apartamento_id=1, area_id=2, data="2024-12-26", tool_context=ctx_unconfirmed)
        assert "Aguardando confirmação" in msg
        assert ctx_unconfirmed.requested_hint is not None

        ctx_confirmed = MockToolContext(confirmed=True)
        msg = tools.functions.reservar_area(apartamento_id=1, area_id=2, data="2024-12-26", tool_context=ctx_confirmed)
        assert "Sucesso" in msg

def test_funcao_cancelar_reserva_sucesso(db_session):
    """Testa cancelamento válido pela própria pessoa."""
    with patch("tools.functions.SessionLocal", return_value=db_session):
        ctx = MockToolContext(user_id="101")
        tools.functions.reservar_area(apartamento_id=1, area_id=1, data="2024-12-24", tool_context=ctx)
        
        reservas = tools.functions.listar_minhas_reservas(tool_context=ctx)
        assert len(reservas) == 1
        
        msg = tools.functions.cancelar_reserva(reserva_id=reservas[0]["id"], tool_context=ctx)
        assert "Sucesso" in msg
        
        reservas_depois = tools.functions.listar_minhas_reservas(tool_context=ctx)
        assert len(reservas_depois) == 0

def test_funcao_cancelar_reserva_falha_seguranca(db_session):
    """Testa cancelamento inválido (Garantia 4)."""
    with patch("tools.functions.SessionLocal", return_value=db_session):
        ctx_101 = MockToolContext(user_id="101")
        tools.functions.reservar_area(apartamento_id=1, area_id=1, data="2024-12-24", tool_context=ctx_101)
        reservas = tools.functions.listar_minhas_reservas(tool_context=ctx_101)
        r_id = reservas[0]["id"]
        
        # Apto 102 tenta cancelar
        apto2 = Apartamento(id=2, numero="102")
        db_session.add(apto2)
        db_session.commit()
        
        ctx_102 = MockToolContext(user_id="102")
        msg = tools.functions.cancelar_reserva(reserva_id=r_id, tool_context=ctx_102)
        assert "Erro" in msg
        assert "Falha de segurança" in msg

def test_funcao_autorizar_visitante_sucesso(db_session):
    """Testa o caminho feliz de adicionar visitante"""
    with patch("tools.functions.SessionLocal", return_value=db_session):
        msg = tools.functions.autorizar_visitante(apartamento_id=1, nome="João", documento="123")
        assert "Sucesso" in msg

def test_funcao_autorizar_visitante_limite_excedido(db_session):
    """Testa o fluxo da Garantia 2 (Limite de 3 visitantes)"""
    with patch("tools.functions.SessionLocal", return_value=db_session):
        # Cadastra 3 visitantes
        tools.functions.autorizar_visitante(apartamento_id=1, nome="V1", documento="001")
        tools.functions.autorizar_visitante(apartamento_id=1, nome="V2", documento="002")
        tools.functions.autorizar_visitante(apartamento_id=1, nome="V3", documento="003")
        
        # Tenta o quarto visitante
        msg = tools.functions.autorizar_visitante(apartamento_id=1, nome="V4", documento="004")
        
        assert "Erro" in msg
        assert "Limite atingido" in msg
