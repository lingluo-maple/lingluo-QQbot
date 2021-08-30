import asyncio
import logging

from datetime import datetime
from typing import NoReturn

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.decl_api import declarative_base
from sqlalchemy import  Column, update, select
from sqlalchemy.sql.sqltypes import BigInteger, DateTime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s : %(message)s")

Base = declarative_base()

engine = create_async_engine("mysql+aiomysql://root:123789.ma_59BD67@localhost/group_member", echo=False)

async def query() -> list:
    async with AsyncSession(engine) as session:
        reslt = await session.execute("SELECT uid, qq FROM member;")
        res = []
        for row in reslt:
            logging.info(f"ROW: {row}")
            res.append(str(row))
        return res

async def add_new(member_id) -> bool:
    '''向数据库中添加新成员'''
    async with AsyncSession(engine) as session:
        member = await session.execute(select(Member).where(Member.qq == member_id))
    member_result = member.first()
    if member_result:
        return False
    new_member = Member(qq=member_id, last_send_message_time=datetime.now())
    async with AsyncSession(engine) as session:
        session.add(new_member)
        await session.commit()
    return True

async def update_time(member_id) -> NoReturn:
    '''更新数据库中成员的发言时间'''
    async with AsyncSession(engine) as session:
        await session.execute(update(Member).
                    where(Member.qq==member_id).
                    values(last_send_message_time=datetime.now()))
        await session.commit()

class Member(Base):
    __tablename__ = "member"

    uid = Column(BigInteger, primary_key=True, autoincrement=True)
    qq = Column(BigInteger, nullable=False)
    last_send_message_time = Column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"Member({self.uid}, qq:{self.qq})"

async def main():
    qq = 1556566021
    result = await add_new(qq)
    logging.info(result)

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
