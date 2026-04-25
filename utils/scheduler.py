import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db_instance import db

scheduler = AsyncIOScheduler()

async def workout_remind_print(bot):
    print(f"Напоминалка сработала в {datetime.now()}")
    users = await db.get_all_users()
    for user in users:
        if user.get("reminder_enabled", 1):
            if user.get("goal"):
                try:
                    await bot.send_message(
                        user["user_id"],
                        "Не забывай про тренировки!"
                    )
                    await asyncio.sleep(0.3)
                except Exception as e:
                    print(f"Ошибка отправки юзеру {user['user_id']}: {e}")

def setup_scheduler(bot):
    scheduler.add_job(
        workout_remind_print,
        'cron',
        hour=15,
        minute=0,
        args=[bot]
    )
    scheduler.start()
    print("Планировщик запущен, задача на 15:00 добавлена")