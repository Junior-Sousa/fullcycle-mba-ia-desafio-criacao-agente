import uvicorn
import sys
from pathlib import Path

# Adiciona a raiz do projeto no sys.path para permitir importação da pasta 'scripts'
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.setup import setup_env, setup_database

if __name__ == "__main__":
    print("=== Verificando Setup Inicial ===")
    setup_env()
    setup_database()
    
    print("\n=== Iniciando API do Residencial Aurora ===")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
