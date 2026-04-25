import sqlite3
import asyncio
from typing import Optional, Dict, List
from logger import logger

class Database:
    def __init__(self, db_path="data.db"):
        self.db_path = db_path
        self._lock = asyncio.Lock()
        self._create_tables()

    def _create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    goal TEXT,
                    streak INTEGER DEFAULT 0,
                    last_workout_date TEXT,
                    total_workouts INTEGER DEFAULT 0,
                    level TEXT DEFAULT 'easy',
                    workouts_on_level INTEGER DEFAULT 0,
                    gender TEXT,
                    gym_level TEXT DEFAULT 'pro1',
                    gym_workouts_count INTEGER DEFAULT 0,
                    gym_daily_count INTEGER DEFAULT 0,
                    gym_last_workout_date TEXT
                )
            ''')
            cur.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cur.fetchall()]
            if "reminder_enabled" not in columns:
                cur.execute("ALTER TABLE users ADD COLUMN reminder_enabled INTEGER DEFAULT 1")
            conn.commit()

    async def _run_sync(self, func, *args, **kwargs):
        async with self._lock:
            return await asyncio.to_thread(func, *args, **kwargs)

    def _get_user_sync(self, user_id: int) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    async def get_user(self, user_id: int) -> Optional[Dict]:
        try:
            return await self._run_sync(self._get_user_sync, user_id)
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {user_id}: {e}")
            return None

    def _save_user_sync(self, user_data: Dict):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT OR REPLACE INTO users (
                    user_id, username, first_name, goal, streak, last_workout_date,
                    total_workouts, level, workouts_on_level, gender, gym_level,
                    gym_workouts_count, gym_daily_count, gym_last_workout_date,
                    reminder_enabled
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data.get('user_id'),
                user_data.get('username'),
                user_data.get('first_name'),
                user_data.get('goal'),
                user_data.get('streak', 0),
                user_data.get('last_workout_date'),
                user_data.get('total_workouts', 0),
                user_data.get('level', 'easy'),
                user_data.get('workouts_on_level', 0),
                user_data.get('gender'),
                user_data.get('gym_level', 'pro1'),
                user_data.get('gym_workouts_count', 0),
                user_data.get('gym_daily_count', 0),
                user_data.get('gym_last_workout_date'),
                user_data.get('reminder_enabled', 1)
            ))
            conn.commit()

    async def save_user(self, user_data: Dict):
        try:
            await self._run_sync(self._save_user_sync, user_data)
        except Exception as e:
            logger.error(f"Ошибка сохранения пользователя {user_data.get('user_id')}: {e}")

    def _update_user_sync(self, user_id: int, **kwargs):
        allowed_fields = {
            "username", "first_name", "goal", "streak", "last_workout_date",
            "total_workouts", "level", "workouts_on_level", "gender",
            "gym_level", "gym_workouts_count", "gym_daily_count", "gym_last_workout_date",
            "reminder_enabled"
        }
        fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not fields:
            return
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            set_clause = ", ".join([f"{key} = ?" for key in fields])
            values = list(fields.values()) + [user_id]
            cur.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
            conn.commit()

    async def update_user(self, user_id: int, **kwargs):
        try:
            await self._run_sync(self._update_user_sync, user_id, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка обновления пользователя {user_id}: {e}")

    def _get_all_users_sync(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT * FROM users")
            rows = cur.fetchall()
            return [dict(row) for row in rows]

    async def get_all_users(self) -> List[Dict]:
        try:
            return await self._run_sync(self._get_all_users_sync)
        except Exception as e:
            logger.error(f"Ошибка получения всех пользователей: {e}")
            return []

    def _delete_user_sync(self, user_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()

    async def delete_user(self, user_id: int):
        try:
            await self._run_sync(self._delete_user_sync, user_id)
        except Exception as e:
            logger.error(f"Ошибка удаления пользователя {user_id}: {e}")