import uuid
from datetime import datetime, timedelta, timezone
import psycopg
from lib import db


class CreateActivity:
    def run(message, user_handle, ttl):
        model = {
          'errors': None,
          'data': None
        }

        now = datetime.now(timezone.utc).astimezone()

        ttl_dict = {
          '30-days': timedelta(days=30),
          '7-days': timedelta(days=7),
          '3-days': timedelta(days=3),
          '1-day': timedelta(days=1),
          '12-hours': timedelta(hours=12),
          '3-hours': timedelta(hours=3),
          '1-hour': timedelta(hours=1)
        }

        if ttl in ttl_dict:
            ttl_offset = ttl_dict[ttl]
        else:
            model['errors'] = ['ttl_blank']


        if user_handle is None or len(user_handle) < 1:
            model['errors'] = ['user_handle_blank']

        if message is None or len(message) < 1:
            model['errors'] = ['message_blank'] 
        elif len(message) > 280:
            model['errors'] = ['message_exceed_max_chars'] 

        if model['errors']:
            model['data'] = {
              'handle':  user_handle,
              'message': message
            }   
        else:
            model['data'] = {
              'uuid': uuid.uuid4(),
              'display_name': 'Andrew Brown',
              'handle':  user_handle,
              'message': message,
              'created_at': now.isoformat(),
              'expires_at': (now + ttl_offset).isoformat()
            }
        return model

    def create_activity(handle, message, expires_at):
        sql = f"""
        INSERT INTO public.activities (user_uuid, message, expires_at)
        VALUES ((SELECT uuid FROM public.users WHERE users.handle = %(handle)s LIMIT 1), %(message)s, %(expires_at)s RETURNING uuid;
        """
        uuid = database_manipulator.query_commit(sql, handle=handle, message=message, expires_at=expires_at)
        try:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    print(f"cursor object: {cur}")
                    cur.execute(sql)
                    conn.commit()
        except OperationalError as error:
            database_manipulator.print_psycopg2_exception(error)
            conn.close()
        except Exception as error:
            database_manipulator.print_psycopg2_exception(error)

            # conn.rollback()