import aiosqlite
from src.services.adk_runner import runner

class SessionService:
    @staticmethod
    async def get_user_id(session_id: str) -> str | None:
        user_id = None
        db_path = runner.session_service._db_connect_path
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT user_id FROM sessions WHERE id = ?", (session_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    user_id = row[0]
        return user_id
