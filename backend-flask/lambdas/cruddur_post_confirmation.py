import json
import os
import psycopg2  # should this be version 3?

def lambda_handler(event, context):
    user = event['request']['userAttributes']
    try:
        conn = psycopg2.connect(os.getenv("CONNECTION_URL"))
        cur = conn.cursor()
        cur.execute(f"""INSERT INTO public.users (display_name, handle, email, cognito_user_id)
                    VALUES (
                    '{user['name']}',
                    '{user['preferred_username']}',
                    '{user['email']}',
                    '{user['sub']}')"""
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