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

def test_funcao_reservar_area_sucesso(db_session):
    """Testa o caminho feliz de uma reserva"""
    with patch("tools.functions.SessionLocal", return_value=db_session):
        msg = tools.functions.reservar_area(apartamento_id=1, area_id=1, data="2024-12-24")
        assert "Sucesso" in msg

def test_funcao_reservar_area_falha_dupla(db_session):
    """Testa o fluxo da Garantia 5 pela visão da Função (Agente)"""
    with patch("tools.functions.SessionLocal", return_value=db_session):
        # Primeira reserva (sucesso)
        tools.functions.reservar_area(apartamento_id=1, area_id=1, data="2024-12-25")
        
        # Segunda reserva no mesmo dia (deve ser engolida e retornar texto amigável)
        msg = tools.functions.reservar_area(apartamento_id=1, area_id=1, data="2024-12-25")
        
        assert "Erro" in msg
        assert "já está reservada" in msg

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
