import os
import sys
import psycopg2  # version 2 needed to use compiled psycopg layer


def lambda_handler(event, context):
    user = event['request']['userAttributes']
    print(f"Attributes: {user['name']}, {user['email']}, {user['preferred_username']}, {user['sub']}")
    try:
        print('entered try stmt')
        sql = f"""INSERT INTO public.users (display_name, handle, email, cognito_user_id)
                    VALUES (%s, %s, %s, %s)"""
        conn_url = os.getenv("PROD_CONNECTION_URL")
        print("Attempting psycopg2 connection to ...")
        conn = psycopg2.connect(conn_url)
        print("psycopg2 connection established")
        cur = conn.cursor()
        cur.execute(sql, (user['name'], user['preferred_username'], user['email'], user['sub']))
        conn.commit()
    except psycopg2.OperationalError as error:
        print(f"Unable to establish connection:\n {print_psycopg2_exception(error)}")
        conn = None
    except (Exception, psycopg2.DatabaseError) as error:
        print_psycopg2_exception(error)
        conn = None
    finally:
        # if connection was established, then it will be closed
        if conn:
            cur.close()
            conn.close()
            print("Database connection closed.")
    return event


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
