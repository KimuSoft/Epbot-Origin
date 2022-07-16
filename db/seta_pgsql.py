import asyncio
import json
import sys

import aiopg

import config
from utils import logger
from utils.asynchelper import synchronize_async_helper

if sys.version_info >= (3, 8) and sys.platform.lower().startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

pool = synchronize_async_helper(aiopg.create_pool(dsn=config.PG_DSN).__aenter__())


class S_PgSQL:
    async def update_sql(self, table: str, rec: str, where: str = "", commit=True):
        """
        설명 : 조건에 맞는 행의 내용을 수정함
        update_sql(테이블명, 수정할 열의 이름과 값, 수정할 행의 조건, DB 경로)
        ※ '수정할 행의 조건'은 생략 가능
        ※ 파일이 없는 경우 False 반환(그 외의 경우 True 반환)

        ---- EXAMPLE ----
        > seta_sqlite.update_sql('테이블', "kimu=3", "kawaii=1", '키뮤.sql')
        """

        if where != "" and not where.startswith("WHERE"):
            where = "WHERE " + where
        await self.sql(f"UPDATE {table} SET {rec} {where}", commit=commit)
        return True

    async def insert_sql(self, table: str, rec: str, val: str, commit=True):
        """
        설명 : 행을 추가함
        insertsql(테이블명, 입력할 열들(A, B), 값들(a, B) , DB 경로)
        ※ 파일이 없는 경우 False 반환(그 외의 경우 True 반환)

        ---- EXAMPLE ----
        > seta_sqlite.insert_sql('테이블', "kimu, seta", "'kawaii', 4", '키뮤.sql')
        → 테이블의 kimu 열에 kawaii, seta 열에 4 값이 들어간 행이 추가됨
        """
        await self.sql(
            "INSERT INTO " + table + " (" + rec + ") VALUES (" + val + ")",
            commit=commit,
        )

    async def insert_dict(self, table: str, dictionary: dict):
        columns = ", ".join(dictionary.keys())
        values = [self.autoquotes(i) for i in dictionary.values()]
        values = ", ".join(values)
        statement = "INSERT INTO " + table + f" ({columns}) VALUES ({values})"
        logger.query(statement)
        await self.sql(statement, commit=True, reading=False)

    async def select_sql(self, table: str, rec: str, rule: str = ""):
        """
        설명 : (조건에 맞는) 행의 내용을 불러옴
        selectsql(테이블명, 불러올 열의 이름, 불러올 행의 조건, DB 경로)
        ※ 파일이 없는 경우 False 반환
        ※ 조건에 맞는 행이 없으면 빈 리스트([])를 반환

        ---- EXAMPLE ----
        > seta_sqlite.select_sql('테이블', "kimu, seta", "kimu=1", '키뮤.sql')
        → 테이블에서 kimu 값이 1인 행에서 kimu, seta열 값을 모두 받아옴.S
        """
        if rule != "" and not rule.startswith("WHERE") and not rule.startswith("ORDER"):
            rule = "WHERE " + rule
        return await self.sql("SELECT " + rec + " FROM " + table + " " + rule, True)

    async def delete_sql(self, table: str, rule: str):
        """
        설명 : 조건에 맞는 행을 삭제함
        delete_sql(테이블명, 삭제할 행의 조건, DB 경로)

        ---- EXAMPLE ----
        > seta_sqlite.delete_sql('테이블', "WHERE kimu=1", '키뮤.sql')
        """
        await self.sql("DELETE FROM " + table + " " + rule)

    async def is_sql(self, table: str, rule: str = ""):
        """
        설명 : 조건에 맞는 행이 있는 지의 여부(True, False)를 반환함
        is_sql(테이블명, 조건, DB 경로)

        ---- EXAMPLE ----
        > seta_sqlite.is_sql('테이블', "WHERE kimu=1", '키뮤.sql')
        """
        result = await self.sql(
            "select exists(select * from " + table + " " + rule + ")", True
        )
        return result[0][0]

    async def sql(self, qur, reading=False, commit=True):
        """
        설명 : SQL문을 사용함
        sql(SQL쿼리, DB 경로, writing)

        ※ rt 설명
        reading True이면 fetchall로 결과를 반환
        reading False이면 결과를 반환하지 않고 commit함.
        """
        async with pool.acquire() as conn:
            logger.query(qur)
            async with conn.cursor() as cur:
                if reading:
                    await cur.execute(qur)

                    return await cur.fetchall()
                elif commit:
                    await cur.execute(qur)

    def autoquotes(self, value):
        if isinstance(value, int):
            return str(value)
        else:
            value = "'" + str(value).replace('"', "\\'") + "'"
            return value

    def json_convert(self, val):
        res = json.dumps(val, ensure_ascii=False)
        return res
