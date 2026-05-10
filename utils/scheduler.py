import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db_instance import db

scheduler = AsyncIOScheduler()

async def workout_remind_print(bot):
    print(f"Напоминалка сработала в {datetime.now()}")
    users = await db.get_all_users()
    for user in users:
        if user.get("reminder_enabled", 1) and user.get("goal"):
            try:
                await bot.send_message(user["user_id"], "Не забывай про тренировки!")
                await asyncio.sleep(0.3)
            except Exception as e:
                print(f"Ошибка отправки пользователю {user['user_id']}: {e}")

#очистка логов старше 5 дней
async def clean_old_logs():
    log_dir = Path(__file__).parent.parent / "logs"
    if not log_dir.exists():
        return
    now = datetime.now()
    for log_file in log_dir.glob("bot.log*"):
        try:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if now - mtime > timedelta(days=5):
                log_file.unlink()
                print(f"Удалён старый лог: {log_file.name}")
        except Exception as e:
            print(f"Ошибка при удалении {log_file.name}: {e}")

def setup_scheduler(bot):
    scheduler.add_job(workout_remind_print, 'cron', hour=15, minute=0, args=[bot])
    scheduler.add_job(clean_old_logs, 'cron', hour=3, minute=0)  # каждый день в 3:00
    scheduler.start()
    print("Планировщик запущен, задачи добавлены")