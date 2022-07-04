import sqlite3
from utils import logger


class S_SQLite:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.cur = self.conn.cursor()

    def update_sql(self, table: str, rec: str, where: str = "", commit=True):
        """
        설명 : 조건에 맞는 행의 내용을 수정함
        update_sql(테이블명, 수정할 열의 이름과 값, 수정할 행의 조건, DB 경로)
        ※ '수정할 행의 조건'은 생략 가능
        ※ 파일이 없는 경우 False 반환(그 외의 경우 True 반환)

        ---- EXAMPLE ----
        > seta_sqlite.update_sql('테이블', "kimu=3", "kawaii=1", '키뮤.sql')
        """

        if not where == "":
            where = " WHERE " + where
        self.sql("UPDATE " + table + " SET " + rec + where, commit=commit)
        return True

    def insert_sql(self, table: str, rec: str, val: str, commit=True):
        """
        설명 : 행을 추가함
        insertsql(테이블명, 입력할 열들(A, B), 값들(a, B) , DB 경로)
        ※ 파일이 없는 경우 False 반환(그 외의 경우 True 반환)

        ---- EXAMPLE ----
        > seta_sqlite.insert_sql('테이블', "kimu, seta", "'kawaii', 4", '키뮤.sql')
        → 테이블의 kimu 열에 kawaii, seta 열에 4 값이 들어간 행이 추가됨
        """
        self.sql(
            "INSERT into " + table + " (" + rec + ") VALUES (" + val + ")",
            commit=commit,
        )
        return True

    def select_sql(self, table: str, rec: str, rule: str = ""):
        """
        설명 : (조건에 맞는) 행의 내용을 불러옴
        selectsql(테이블명, 불러올 열의 이름, 불러올 행의 조건, DB 경로)
        ※ 파일이 없는 경우 False 반환
        ※ 조건에 맞는 행이 없으면 빈 리스트([])를 반환

        ---- EXAMPLE ----
        > seta_sqlite.select_sql('테이블', "kimu, seta", "WHERE kimu=1", '키뮤.sql')
        → 테이블에서 kimu 값이 1인 행에서 kimu, seta열 값을 모두 받아옴.
        """
        return self.sql("SELECT " + rec + " FROM " + table + " " + rule, True)

    def delete_sql(self, table: str, rule: str):
        """
        설명 : 조건에 맞는 행을 삭제함
        delete_sql(테이블명, 삭제할 행의 조건, DB 경로)

        ---- EXAMPLE ----
        > seta_sqlite.delete_sql('테이블', "WHERE kimu=1", '키뮤.sql')
        """
        self.sql("DELETE FROM " + table + " " + rule)

    def is_sql(self, table: str, rule: str = ""):
        """
        설명 : 조건에 맞는 행이 있는 지의 여부(True, False)를 반환함
        is_sql(테이블명, 조건, DB 경로)

        ---- EXAMPLE ----
        > seta_sqlite.is_sql('테이블', "WHERE kimu=1", '키뮤.sql')
        """
        result = self.sql(
            "select exists(select * from " + table + " " + rule + ")", True
        )
        return result[0][0]

    def sql(self, qur, reading=False, commit=True):
        """
        설명 : SQL문을 사용함
        sql(SQL쿼리, DB 경로, writing)

        ※ rt 설명
        reading True이면 fetchall로 결과를 반환
        reading False이면 결과를 반환하지 않고 commit함.
        """
        logger.query(qur)
        try:
            self.cur.execute(qur)
        except Exception as e:
            logger.err(e)

        if reading:
            return self.cur.fetchall()
        elif commit:
            self.conn.commit()

    def commit(self):
        self.conn.commit()
