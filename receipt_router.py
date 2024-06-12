from datetime import datetime
import os

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from database import orm
from filters.admin import IsInGroup
from sheets.sheets import fill_table, get_current_time


load_dotenv(find_dotenv())

receipt_router = Router()
receipt_router.message.filter(IsInGroup())


@receipt_router.message(F.photo)
async def wait_for_check(message: Message, bot: Bot, session: AsyncSession):
    try:
        msg = message.reply_to_message

        if msg.from_user.id == bot.id:

            current_datetime = datetime.now()
            date = current_datetime.strftime("%d-%m-%Y")
            first_str = msg.text.split("\n")[0]

            cur_number, exchanger = first_str.split(' || ')
            if exchanger == 'Transit-Bit':
                chat_id = os.getenv('TRANSIT_CHAT_ID')
            else:
                chat_id = os.getenv('GOODBOY_CHAT_ID')
            caption = f'{cur_number} || {date}'
            await bot.send_photo(chat_id=chat_id,
                                 photo=message.photo[-1].file_id,
                                 caption=caption)
            exchange = await orm.get_exchange(
                session, message_id=msg.message_id)
            try:
                fill_table(exchanger=exchanger,
                           usdt=exchange.usdt,
                           rub=exchange.rub)
            except Exception as e:
                await bot.send_message(
                    chat_id=os.getenv('ADMIN_ID'),
                    text=(f'Ошибка при заполнении таблицы:\n{e}\n'
                          f'{get_current_time("time")}'))
            await orm.del_exchange(session, message_id=msg.message_id)
    except AttributeError:
        return


@receipt_router.message(Command('new'))
async def get_new_exchanges(message: Message, session: AsyncSession):
    exchanges = await orm.get_exchanges(session)
    if exchanges == []:
        await message.answer(text='Все заявки оплачены')
    else:
        for index, exchange in enumerate(exchanges):
            await message.answer(text=f'{index + 1} || {exchange.exchanger}',
                                 reply_to_message_id=exchange.message_id)


@receipt_router.message(Command('drop_t'))
async def drop_transit(message: Message, session: AsyncSession):
    await orm.drop_exchanges(session, exchanger='Transit-Bit')
    await message.answer(text='Сброс заявок transit-bit')


@receipt_router.message(Command('drop_g'))
async def drop_goodboy(message: Message, session: AsyncSession):
    await orm.drop_exchanges(session, exchanger='GoodBoy')
    await message.answer(text='Сброс заявок goodboyswap')


@receipt_router.message(Command('drop'))
async def drop(message: Message, session: AsyncSession):
    await orm.drop_all(session)
    await message.answer(text='Сброс всех заявок')
