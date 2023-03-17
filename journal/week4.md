# Week 4 — Postgres and RDS
## Create RDS Instance
* In a terminal execute the following code:
```sh
aws rds create-db-instance \
--db-instance-identifier cruddur-db-instance \
--db-instance-class db.t3.micro \
--engine postgres \
--engine-version 14.6 \
--master-username <db_username> \
--master-user-password <db_password> \
--allocated-storage 20 \
--availability-zone us-east-2c \
--backup-retention-period 0 \
--port 5432 \
--no-multi-az \
--db-name cruddur \
--storage-type gp2 \
--publicly-accessible \
--storage-encrypted \
--enable-performance-insights \
--performance-insights-retention-period 7 \
--no-deletion-protection
```

* stop DB instance

![HINT pic of DB instance stopped temporarily]()

## Create scripts and other files to create database, tables, schema
```sh
mkdir backend-flask/db
touch backend-flask/db/schema.sql backend-flask/db/seed.sql
mkdir backend-flask/bin
touch backend-flask/bin/db-create backend-flask/bin/db-drop \
backend-flask/bin/db-seed backend-flask/bin/db-schema-load \
backend-flask/bin/db-connect backend-flask/bin/db-sessions \
backend-flask/bin/db-setup
```
* Add UUID extension to *backend-flask/db/schema.sql*
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
psql cruddur < backend-flask/db/schema.sql -h localhost -U postgres
```
* Create envronment variables
```sh
export CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
PROD_CONNECTION_URL="postgresql://cruddur_root:SomeType0fPas5w0rD@localhost:5432/cruddur"
```
* Add shebang and color coding to files in *backend-flask/bin* directory
```sh
for file in ./backend-flask/bin/*; do \
echo -e "#!""$(which bash)\n\n\
CYAN='\033[1;36m'\nNO_COLOR='\033[0m'\n\
LABEL=$file\nprintf \"\
\${CYAN}== \${LABEL}\${NO_COLOR} \"\n" > $file; done
```

* in *backend-flask/bin/db-drop* append
```sh
NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<< $CONNECTION_URL)
psql $NO_DB_CONNECTION_URL -c "drop database cruddur;"
```
* in *backend-flask/bin/db-create* append
```sh
NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<< $CONNECTION_URL)
psql $NO_DB_CONNECTION_URL -c "create database cruddur;"
```
* in *backend-flask/bin/db-schema-load* append
```sh
schema_path=$(realpath ./backend-flask/db/schema.sql)

if [ "$1" = "prod" ]; then
  echo "Using the Prod environment"
  CON_URL=$PROD_CONNECTION_URL
else
  echo "This is the Development environment"
  CON_URL=$CONNECTION_URL
fi

psql $CON_URL cruddur < $schema_path
```
* Change permissions of files/scripts, make them executable for user
```sh
chmod -Rv u+x ./backend-flask/bin/*
```
## Construct schema for database
* in *backend-flask/db/schema.sql* append:
```sql
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.activities;

CREATE TABLE public.users (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  display_name text,
  handle text,
  cognito_user_id text,
  create_at TIMESTAMP default current_timestamp NOT NULL
);


CREATE TABLE public.activities (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_uuid UUID NOT NULL,
  message text NOT NULL,
  replies_count integer DEFAULT 0,
  reposts_count integer DEFAULT 0,
  likes_count integer DEFAULT 0,
  reply_to_activity_uuid integer,
  expires_at TIMESTAMP,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
```
** in postgres schema refers to different namespaces

## Seed (provide mock) data
* in *backend-flask/bin/db-seed* append

```sh
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL='db-seed'
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

seed_path=$(realpath ./backend-flask/db/seed.sql)

if [ "$1" = "prod" ]; then
  echo "Using the Prod environment"
  CON_URL=$PROD_CONNECTION_URL
else
  echo "This is the Development environment"
  CON_URL=$CONNECTION_URL
fi

psql $CON_URL cruddur < $seed_path
```
* append this to *backend-flask/db/seed.sql*
```sql
insert into public.users (display_name, handle, cognito_user_id)
values
  ('Pop Goes the Weasel', 'hotwheels', 'MOCK'),
  ('Fifty Pence', 'getFullOrDieTryin', 'MOCK');

insert into public.activities (user_uuid, message, expires_at)
  values (
    (select uuid from public.users where users.handle = 'hotwheels' limit 1),
    'This was imported as seed data',
    current_timestamp + interval '10 day'
  );
```
* Create db connect script
- in *backend-flask/bin/db-connect* append
```sh
NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<< $CONNECTION_URL)
psql $NO_DB_CONNECTION_URL
```
* Check if any active database connections are present
- in *backend-flask/bin/db-sessions* append:

```sh
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL='db-sessions'
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

if [ "$1" = "prod" ]; then
  echo "Using the Prod environment"
  URL=$PROD_CONNECTION_URL
else
  echo "This is the Development environment"
  URL=$CONNECTION_URL
fi

NO_DB_CON_URL=$(sed 's/\/cruddur//g' <<< $URL)
psql $NO_DB_CON_URL -c "select pid as process_id, \
    username user,
    datname db, \
    client_addr, \
    application_name app, \
    state \
from pg_stat_activity;"
