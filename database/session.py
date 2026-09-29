from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# Banco de dados na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "condominio.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False é necessário pois o FastAPI pode usar múltiplas threads no SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para os modelos (tabelas)
Base = declarative_base()

# Dependência do FastAPI para injetar a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
