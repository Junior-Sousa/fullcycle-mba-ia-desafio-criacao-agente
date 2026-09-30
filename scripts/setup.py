import os
import sys
import json
import shutil
from pathlib import Path

# Adiciona a raiz do projeto ao PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

ENV_FILE = BASE_DIR / ".env"
ENV_EXAMPLE = BASE_DIR / ".env.example"

def setup_env():
    print("=== Configuração do Ambiente ===")
    if not ENV_FILE.exists():
        print("Criando arquivo .env a partir de .env.example...")
        shutil.copy(ENV_EXAMPLE, ENV_FILE)
        print("⚠️ IMPORTANTE: Um arquivo .env foi criado. Por favor, preencha a variável GEMINI_API_KEY no arquivo .env antes de rodar a API.")
    else:
        print("Arquivo .env já existe.")

def setup_database():
    print("\n=== Restauração do Banco de Dados ===")
    
    # Importa módulos locais do projeto
    from src.database.session import Base, engine, SessionLocal
    from src.models import Apartamento, Area, Reserva, Visitante

    # Apaga os bancos de dados antigos para garantir um restore limpo
    DB_PATH = BASE_DIR / 'condominio.db'
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Banco de dados antigo apagado: {DB_PATH}")
        
    ADK_DB_PATH = BASE_DIR / 'adk_session.db'
    if ADK_DB_PATH.exists():
        ADK_DB_PATH.unlink()
        print(f"Banco de dados de sessões apagado: {ADK_DB_PATH}")

    # Cria todas as tabelas
    Base.metadata.create_all(bind=engine)
    print("Banco de Dados inicializado com as tabelas da aplicação.")

    db = SessionLocal()

    def carregar_json(nome_arquivo):
        caminho = BASE_DIR / "dados" / nome_arquivo
        if not caminho.exists():
            print(f"Arquivo não encontrado: {caminho}")
            return []
        with open(caminho, 'r', encoding='utf-8') as f:
            return json.load(f)

    try:
        print("Inserindo apartamentos...")
        apartamentos_dados = carregar_json("apartamentos.json")
        for apto in apartamentos_dados:
            db.add(Apartamento(numero=apto["numero"], morador=apto["morador"]))
        db.commit()

        print("Inserindo áreas comuns...")
        areas_dados = carregar_json("areas.json")
        for area in areas_dados:
            db.add(Area(id=area["id"], nome=area["nome"], taxa=area["taxa"]))
        db.commit()

        print("Inserindo reservas...")
        reservas_dados = carregar_json("reservas.json")
        for res in reservas_dados:
            db.add(Reserva(codigo=res["codigo"], apartamento=res["apartamento"], area=res["area"], data=res["data"]))
        db.commit()

        print("Inserindo visitantes...")
        visitantes_dados = carregar_json("visitantes.json")
        for vis in visitantes_dados:
            db.add(Visitante(apartamento=vis["apartamento"], nome=vis["nome"], data=vis["data"]))
        db.commit()

        print("\n✅ Setup e restauração concluídos com sucesso! O estado original foi carregado.")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro durante a restauração: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    setup_env()
    setup_database()
