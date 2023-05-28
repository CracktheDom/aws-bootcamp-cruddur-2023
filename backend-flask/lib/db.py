import os
import sys
import psycopg2
from psycopg_pool import ConnectionPool


class DatabaseManipulator:
    def __init__(self):
      """Initializes object, and Connection Pool to Postgres database"""
        self.connection_url = os.getenv('CONNECTION_URL')
        self.pool = ConnectionPool(self.connection_url)

    def query_commit(self, sql, **kwargs) -> str:
        print('\n \033[95m SQL STMT with returning ID \033[0m')
        try:
            conn = self.pool.connection()
            cur = conn.cursor()
            print(f"cursor object: {cur}")
            cur.execute(sql, **kwargs)  # timestamp 41:00
            if 'RETURNING' in sql or 'returning' in sql:
                returning_id = cur.fetchone()[0]
                conn.commit()
                return returning_id
            conn.commit()
        except Exception as e:
            print_psycopg2_exception(e)

    def query_object_json(self, sql):
        """Returns a JSON object"""
        wrapped_sql = self.query_wrap_object(sql)
        with self.connection() as conn:
            with conn.cursor() as cur:
                print(f"cursor object: {cur}")
                cur.execute(wrapped_sql)
                return cur.fetchone()[0]

    def query_array_json(self, sql):
        """Returns an list/array of JSON objects"""
        wrapped_sql = self.query_wrap_array(sql)
        with self.connection() as conn:
            with conn.cursor() as cur:
                print(f"cursor object: {cur}")
                cur.execute(wrapped_sql)
                return cur.fetchall()  # or .fetchone[0]?

    @staticmethod
    def print_psycopg2_exception(err):
        # get details about the exception
        err_type, _, traceback = sys.exc_info()

        # get line number of when exception occurred
        line_num = traceback.tb_lineno

        # print the connect() error
        print(f"\npsycopg2 ERROR: {err} on line number: {line_num}")
        print(f"psycopg2 traceback: {traceback} -- type {err_type}")

        # psycopg2 extensions.Diagnostics object attribute
        # print(f"\nextensions.Diagnostics: {err.diag}")

        # print the pgcode and pgerror exceptions
        print(f"pgerror: {err.pgerror}")
        print(f"pgcode: {err.pgcode} \n")

    def query_wrap_object(template):
        """ Postgres docs """
        sql = f"""
        (SELECT COALESCE(row_to_json(object_row), '{{}}'::json) FROM (
        {template}
        ) object_row);
        """
        return sql

    def query_wrap_array(template):
        sql = f"""
        (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))), '[]'::json) FROM (
        {template}
        ) array_row);
        """
        return sql


database_manipulator = DatabaseManipulator()
