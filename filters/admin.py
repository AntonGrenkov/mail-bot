import os

from aiogram import types
from aiogram.filters import Filter
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class IsInGroup(Filter):
    def __init__(self) -> None:
        self.chat_id = int(os.getenv('CHAT_ID'))

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.id == self.chat_id
