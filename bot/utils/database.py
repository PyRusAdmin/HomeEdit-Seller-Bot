"""
Модуль для работы с базой данных
"""

# Пример использования с SQLAlchemy и aiosqlite
# import asyncio
# from sqlalchemy import text
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker

# class Database:
#     def __init__(self, database_url: str):
#         self.engine = create_async_engine(database_url)
#         self.async_session = sessionmaker(
#             self.engine, class_=AsyncSession, expire_on_commit=False
#         )

#     async def init_db(self):
#         async with self.engine.begin() as conn:
#             await conn.run_sync(create_tables)  # функция create_tables должна быть определена

#     async def get_session(self) -> AsyncSession:
#         async with self.async_session() as session:
#             return session

#     async def close(self):
#         await self.engine.dispose()