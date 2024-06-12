import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.exceptions import TelegramConflictError
from dotenv import find_dotenv, load_dotenv

from database.engine import create_db, drop_db, session_maker
from mail import process_email
from middleware.db import DataBaseSession
from receipt_router import receipt_router
from sheets.sheets import get_current_time


load_dotenv(find_dotenv())

TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()
dp.include_routers(
    receipt_router
)


async def polling_mail():
    while True:
        try:
            await process_email(bot=bot,
                                session=session_maker(),
                                exchanger='Transit-Bit')
            await process_email(bot=bot,
                                session=session_maker(),
                                exchanger='GoodBoy')
            await asyncio.sleep(40)
        except Exception as e:
            await bot.send_message(
                  text=(f'Ошибка в работе функции polling_mail\n{e}\n'
                        f'{get_current_time("time")}'),
                  chat_id=os.getenv('ADMIN_ID'))
            await asyncio.sleep(10)


async def start_polling_mail_task():
    while True:
        try:
            await polling_mail()
        except Exception as e:
            await bot.send_message(
                  text=(f'Ошибка в работе функции start_polling_mail\n{e}\n'
                        f'{get_current_time("time")}'),
                  chat_id=os.getenv('ADMIN_ID'))
            await asyncio.sleep(10)


async def on_startup(bot):

    need_drop = False
    if need_drop:
        await drop_db()

    await create_db()
    await bot.send_message(
                  text=(f'Бот начал работу\n'
                        f'{get_current_time("time")}'),
                  chat_id=os.getenv('ADMIN_ID'))


async def on_shutdown(bot):
    await bot.send_message(
                  text=(f'Бот остановлен\n'
                        f'{get_current_time("time")}'),
                  chat_id=os.getenv('ADMIN_ID'))


async def main():

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    backgrounds_tasks = set()
    polling_mail_task = asyncio.create_task(start_polling_mail_task())
    backgrounds_tasks.add(polling_mail_task)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot,
                               allowed_updates=dp.resolve_used_update_types())
    except TelegramConflictError:
        bot.send_message(
            text=(f"Ошибка: Конфликт с другим запросом getUpdates. "
                  f"Включился второй инстанс.\n"
                  f"{get_current_time('time')}"),
            chat_id=os.getenv('ADMIN_ID'))


asyncio.run(main())
