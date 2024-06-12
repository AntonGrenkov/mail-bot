from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Exchange


async def add_exchange(session: AsyncSession,
                       message_id: int,
                       exchanger: str,
                       info_dict: dict):
    query = select(Exchange).where(
        Exchange.message_id == message_id
    )
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            Exchange(
                message_id=message_id,
                exchanger=exchanger,
                usdt=info_dict['usdt'],
                rub=info_dict['rub']
            )
        )
        await session.commit()


async def del_exchange(session: AsyncSession,
                       message_id: int):
    query = delete(Exchange).where(Exchange.message_id == message_id)
    await session.execute(query)
    await session.commit()


async def get_exchange(session: AsyncSession,
                       message_id: int):
    query = select(Exchange).where(Exchange.message_id == message_id)
    result = await session.execute(query)
    return result.scalar()


async def get_exchanges(session: AsyncSession):
    query = select(Exchange)
    result = await session.execute(query)
    return result.scalars().all()


async def get_exchanges_by_name(session: AsyncSession,
                                exchanger: str):
    query = select(Exchange).where(Exchange.exchanger == exchanger)
    result = await session.execute(query)
    return result.scalars().all()


async def drop_exchanges(session: AsyncSession, exchanger: str):
    query = delete(Exchange).where(Exchange.exchanger == exchanger)
    await session.execute(query)
    await session.commit()


async def drop_all(session: AsyncSession):
    query = delete(Exchange)
    await session.execute(query)
    await session.commit()
