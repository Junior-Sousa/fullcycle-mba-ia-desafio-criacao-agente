import os
from google.adk import Runner
from google.adk.sessions.sqlite_session_service import SqliteSessionService
from src.agents.agent import main_agent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STORAGE_PATH = os.path.join(BASE_DIR, "adk_session.db")

sqlite_session_service = SqliteSessionService(db_path=STORAGE_PATH)

runner = Runner(
    agent=main_agent,
    session_service=sqlite_session_service,
    app_name="residencial_aurora"
)
