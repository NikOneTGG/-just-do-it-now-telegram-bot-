#from aiogram.types import Message, FSInputFile
#from aiogram import Bot
#from aiogram.utils.chat_action import ChatActionSender
#
#async def send_video(message: Message, bot: Bot, video_path: str, caption: str = ""):
#    async with ChatActionSender.upload_video(chat_id=message.chat.id):
#        try:
#            video = FSInputFile("")
#            await message.answer_video(video=video, caption=caption)
#        except FileNotFoundError:
#            await message.answer("Видео не найдено. Проверь путь.")
#        except Exception as e:
#            await message.answer(f"Ошибка при отправке видео: {e}")