import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
ENV_EXAMPLE = BASE_DIR / ".env.example"

def setup_env():
    if not ENV_FILE.exists():
        print("Criando arquivo .env a partir de .env.example...")
        shutil.copy(ENV_EXAMPLE, ENV_FILE)
        print("IMPORTANTE: Preencha a chave GEMINI_API_KEY no arquivo .env antes de executar.")
    else:
        print("Arquivo .env já existe.")

def setup_database():
    print("Testando conexão com o banco de dados...")
    
    # Importamos a engine aqui para não dar erro se o ambiente não estiver pronto
    from database.session import engine, Base
    # Precisamos importar os modelos para que o Base.metadata.create_all os reconheça
    import database.models 
    from sqlalchemy import text
    
    try:
        # Cria as tabelas se elas não existirem
        Base.metadata.create_all(bind=engine)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 'Banco de Dados inicializado com as tabelas!'"))
            print(f"Sucesso: {result.scalar()}")
    except Exception as e:
        print(f"Erro ao conectar com o banco: {e}")

if __name__ == "__main__":
    print("=== Iniciando Setup do Ambiente ===")
    setup_env()
    setup_database()
    print("=== Setup Concluído ===")
