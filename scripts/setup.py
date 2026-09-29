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
    print("Inicializando banco de dados... (Será implementado na Fase 2)")
    pass

if __name__ == "__main__":
    print("=== Iniciando Setup do Ambiente ===")
    setup_env()
    setup_database()
    print("=== Setup Concluído ===")
