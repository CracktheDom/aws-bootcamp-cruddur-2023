import json
import os
import psycopg2  # version 2 needed to use compiled psycopg layer

def lambda_handler(event, context):
    user = event['request']['userAttributes']
    try:
        conn = psycopg2.connect(os.getenv("CONNECTION_URL"))
        cur = conn.cursor()
        cur.execute(f"""INSERT INTO public.users (display_name, handle, email, cognito_user_id)
                    VALUES (
                    %(user['name'])s,
                    %(user['preferred_username'])s,
                    %(user['email'])s,
                    %(user['sub'])s)"""
                    )
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn:
            cur.close()
            conn.close()
            print("Database connection closed.")

    return event