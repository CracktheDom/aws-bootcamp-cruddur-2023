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

* stop DB instance via the AWS RDS console

![HINT pic of DB instance stopped temporarily](https://user-images.githubusercontent.com/85846263/229120991-83a00a75-4c76-4690-89be-c547f582bc99.png)

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
```
* Create environment variables for database connection URLs
```sh
export CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
export PROD_CONNECTION_URL="postgresql://cruddur_root:SomeType0fPas5w0rD@localhost:5432/cruddur"
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
* Change the permissions of scripts, make them executable for user
```sh
chmod -Rv u+x backend-flask/bin/*
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
** In Postgres, schema refers to different namespaces **

* Execute the following code in a terminal to test if schema construction is successful
```sh
psql cruddur < backend-flask/db/schema.sql -h localhost -U postgres
```
## Seed (provide mock) data
* in *backend-flask/bin/db-seed* append with the following code

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
### Create database connection script
- in *backend-flask/bin/db-connect* append
```sh
NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<< $CONNECTION_URL)
psql $NO_DB_CONNECTION_URL
```
### Create script to check if any active database connections are present
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
    usename as user,
    datname as db, \
    client_addr, \
    application_name as app, \
    state \
from pg_stat_activity;"

* Create DB setup script
- in *backend-flask/bin/db-setup* append:
```sh
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL='db-sessions'
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

bin_path=$(realpath "$THEIA_WORKSPACE_ROOT/backend-flask/bin")

$bin_path/db-drop
$bin_path/db-create
$bin_path/db-schema-load
$bin_path/db-seed
```
## Connect to RDS Instance
### Need driver to interact with Postgres DB
* add *psycopg[binary]* & *psycopg[pool]* to *backend-flask/requirements.txt*
* execute `python3 -m pip -r requirements.txt` in the *backend-flask* directory

#### Connection Pooling within Postgres

Connection pooling is a technique used to manage and reuse database connections in order to improve the performance, scalability, and efficiency of applications that interact with databases. It involves creating a pool of pre-established database connections that can be reused by multiple client processes or threads instead of creating a new connection for each database request.

* Create a new file
```sh
touch backend-flask/lib/db.py
```

* in *backend-flask/lib/db.py* enter the following
```py
import os
from psycopg_pool import ConnectionPool


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

connection_url = os.getenv("CONNECTION_URL")
pool = ConnectionPool(connection_url)
```

* Delete *results* variable in *backend-flask/services/home_activities.py* and replace with following:
```py
from lib.db import pool, query_wrap_array

...
class HomeActivities:
  def run(cognito_user_id=None):
    ...
    sql = query_wrap_array("""
                           SELECT
                             activities.uuid,
                             users.display_name,
                             users.handle,
                             activities.message,
                             activities.replies_count,
                             activities.reposts_count,
                             activities.likes_count,
                             activities.reply_to_activity_uuid,
                             activities.expires_at,
                             activities.created_at
                           FROM public.activities
                           LEFT JOIN public.users ON users.uuid = activities.user_uuid
                           ORDER BY activities.created_at DESC
                           """)

    with pool.connection() as conn:
      with conn.cursor() as cur:
         cur.execute(sql)  # returns a tuple
         json = cur.fetchone()
    return json[0]
```
### Create new file that will modify database instance security group to allow ingress from GITPOD environment and make file executable for user

```sh
touch backend-flask/bin/rds-update-sg-rule
chmod u+x backend-flask/bin/rds-update-sg-rule
```

* assign username and password for RDS DB to environment variables

```sh
export RDS_DB_USERNAME="cruddur_root"
export RDS_DB_PASSWORD="SomeType0fPas5w0rD"
```

* Retrieve cruddur database security group ID and security group rule ID which are needed to execute command to alter its security group rule
```sh
export DB_SG_ID=`aws rds describe-db-instances --db-instance-identifier cruddur-db-instance --query DBInstances[0].VpcSecurityGroups[0].VpcSecurityGroupId`
export DB_SG_RULE_ID=`aws ec2 describe-security-group-rules --filters Name=group-id,Values=[$DB_SG_ID] --query 'SecurityGroupRules[].SecurityGroupRuleId | [1]'`
```

* Create environment variables for GITPOD environment IP address, cruddur database endpoint
```sh
export GITPOD_IP=$(curl ifconfig.me)
export CRUDDUR_DB_ENDPOINT=`aws rds describe-db-instances --db-instance-identifier cruddur-db-instance --query DBInstances[0].Endpoint.Address --output text`
```

* Modify environment variable to connect with RDS cruddur database instance

```sh
export PROD_CONNECTION_URL="postgresql://${RDS_DB_USERNAME}:${RDS_DB_PASSWORD}@${CRUDDUR_DB_ENDPOINT}:5432/cruddur"
```

* In *backend-flask/bin/rds-update-sg-rule* file, modify DB instance security group to allow traffic from GITPOD environment
```sh
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL='rds-sg-rule'
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

aws ec2 modify-security-group-rules --group-id $DB_SG_ID \
--security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
```

* append the *.gitpod.yml* file with the following code, upon starting up the GITPOD environment, retrieve the newly assigned GITPOD IP address and execute the RDS SG update script to alter RDS security group to allow ingress from GITPOD environment. 
```yml
tasks:
  - name: postgres
    command: |
      export GITPOD_IP=$(curl ifconfig.me)
      $THEIA_WORKSPACE_ROOT/backend-flask/bin/rds-update-sg-rule
```

![pic of RDS SG update script executed](https://github.com/CracktheDom/aws-bootcamp-cruddur-2023/assets/85846263/5e771bac-256c-4830-b774-616dc92f0fd2)

* In the AWS Management console, in the Inbound Rules of the security group for the RDS instance, the new rule will be displayed

![Screenshot_20230318_224850](https://github.com/CracktheDom/aws-bootcamp-cruddur-2023/assets/85846263/8802828b-00bb-499d-9356-b87736e99af1)

### Setup Cognito post confirmation trigger with a Lambda function
#### Create the handler function and Lambda Trigger
* Create Lambda function in the same VPC as RDS instance, in the Lambda console select the Enable VPC option to select VPC that RDS DB instance resides
* paste code into Lambda code section of Management Console
* select the same VPC & choose same subnet as used by RDS instance
* Add environment variables for PROD_CONNECTION_URL with Postgres connection url
* Lambda execution role needs to be created, if it does not exists, to allow for AllowVPCAccess
* Add a layer source, input source ARN or select *Upload from S3* and select zip file
* Add Trigger to Lambda function
* Go to Cognito
* click on *User pool properties* tab
* click on *Add Lambda trigger*
* select *Sign-up* trigger type
* select *Post confirmation trigger*
* select Lambda function in the *Assign Lambda function* section
* click on *Add Lambda trigger*

##### Add a Lambda Layer for psycopg2
* Follow instructions at https://aws.plainenglish.io/creating-aws-lambda-layer-for-python-runtime-1d1bc6c5148d to download psycopg2-binary package, zip it, & upload to S3 bucket
* Create security group for Lambda function that allows egress on port 5432 to security group of RDS instance
* Configure security group of the RDS instance to allow ingress from Lambda function security group on port 5432

  
