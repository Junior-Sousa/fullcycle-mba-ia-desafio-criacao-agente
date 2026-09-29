import sys
from pathlib import Path

# Injeta a raiz do projeto no path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.session import SessionLocal
from database.models import Apartamento, Area, Visitante, Reserva
from scripts.setup import setup_database

def restore_data():
    print("=== Iniciando Restauração de Dados ===")
    
    # GARANTIA: Primeiro executamos o setup para garantir que as tabelas existam
    # independente se o servidor FastAPI está rodando ou não.
    setup_database()
    
    db = SessionLocal()
    try:
        # 1. Limpando o banco de dados (A ordem importa devido as chaves estrangeiras)
        print("1. Limpando tabelas...")
        db.query(Reserva).delete()
        db.query(Visitante).delete()
        db.query(Area).delete()
        db.query(Apartamento).delete()
        db.commit()

        # 2. Inserindo dados originais
        print("2. Inserindo apartamentos iniciais (101 e 102)...")
        apto1 = Apartamento(numero="101")
        apto2 = Apartamento(numero="102")
        db.add_all([apto1, apto2])
        
        print("3. Inserindo áreas comuns (Churrasqueira e Salão de Festas)...")
        area1 = Area(nome="Churrasqueira")
        area2 = Area(nome="Salão de Festas")
        db.add_all([area1, area2])
        
        db.commit()
        print("=== Restauração Concluída com Sucesso ===")
    except Exception as e:
        db.rollback()
        print(f"Erro Crítico durante a restauração: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    restore_data()
