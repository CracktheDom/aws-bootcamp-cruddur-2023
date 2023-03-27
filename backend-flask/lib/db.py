import os
import sys
import psycopg2
from psycopg_pool import ConnectionPool


class DatabaseManipulator:
    def __init__(self):
        self.connection_url = os.getenv('CONNECTION_URL')
        self.pool = ConnectionPool(self.connection_url)


    def init_pool(self):
        pass


    def query_commit_with_returning_id(self, sql, **kwargs):
        print('SQL STMT with returning ID')
        try:
            conn = self.pool.connection()
            cur = conn.cursor()
            print(f"cursor object: {cur}")
            cur.execute(sql, kwargs)
            returning_id = cur.fetchone()[0]
            conn.commit()
            return returning_id
        except Exception as e:
            print_psycopg2_exception(e)


    def query_commit(self, sql):
        """ Commits data such as INSERT command """
        print('SQL STMT commit')
        try:
            conn = self.pool.connection()
            cur = conn.cursor()
            print(f"cursor object: {cur}")
            cur.execute(sql)
        except Exception as e:
            print_psycopg2_exception(e)


    def query_object_json(self, sql):
        """ Returns a JSON object """
        wrapped_sql = self.query_wrap_object(sql)
        with self.connection() as conn:
            with conn.cursor() as cur:
                print(f"cursor object: {cur}")
                cur.execute(sql)
                return cur.fetchone()[0]


    def query_array_json(self, sql):
        """Returns an list/array of JSON objects"""
        wrapped_sql = self.query_wrap_array(sql)
        with self.connection() as conn:
            with conn.cursor() as cur:
                print(f"cursor object: {cur}")
                cur.execute(sql)
                return cur.fetchall()


    def print_psycopg2_exception(err):
        # get details about the exception
        err_type, err_obj, traceback = sys.exc_info()

        # get line number of when exception occurred
        line_num = traceback.tb_lineno

        # print the connect() error
        print(f"\npsycopg2 ERROR: {err} on line number: {line_num}")
        print(f"psycopg2 traceback: {traceback} -- type {err_type}")

        # psycopg2 extensions.Diagnostics object attribute
        print(f'\nextensions.Diagnostics: {err.diag}')

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


dbm = DatabaseManipulator()
