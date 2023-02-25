# Week 1 — App Containerization

## VSCode Docker Extension
Docker for VSCode makes it easy to use Docker

| Gitpod comes preinstalled with extension

## Containerize Backend

### Run Python to start Flask server

```bash
cd backend-flask
export FRONTEND_URL="*"
export BACKEND_URL="*"
python -m flask run --host=0.0.0.0 --port=4567
```
- make sure port 4567 is open/unlocked via Gitpod **PORTS** tab
- click on url in **PORTS** tab
- and append `/api/activities/home` to url
- json object will be visible in browser

![HINT input url for json response](/assets/Screenshot_20230223_020228.png)

### Add Dockerfile

- Create a Dockerfile file here: `touch ./Dockerfile`
- Input the following into file:

```sh
FROM python:3.10-slim-buster

WORKDIR /backend-flask

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_ENV=development

EXPOSE ${PORT}
CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=4567"]
```

#### Build Container

* stop Flask server by pressing `Ctrl + c`
* execute the following commands in the terminal:
```bash
unset FRONTEND_URL
unset BACKEND_URL
cd ..
docker build -t backend-flask:1.0 ./backend-flask
```

execute `docker image ls` to confirm that image was created

![Hint screenshot of docker image command](https://user-images.githubusercontent.com/85846263/221085819-a55b8657-ddc7-446b-a295-b2d1f9702316.png)

### Run Container

```bash
docker run --rm -p 4567:4567 -it backend-flask:1.0
```
* ensure port 4567 is unlocked in the **PORTS** tab in Gitpod
* navigate to url displayed in the **PORTS**
* should see **404 Not Found** page and the server running in terminal should confirm this by displaying the same error code

![404 error](/assets/Screenshot_20230223_155245.png)

* stop container and run again with environment variable parameters
* execute `docker ps` to view running containers with ID's
* execute `docker logs <container id>` to views logs of running container
* **OR** in Docker extension right-click on running container and click on `Attach Shell` to activate shell & execute commands within the container
* within container execute `env | grep _URL` to verify syntax of above was incorrect and did not pass env to container

![screenshot of environment variable not set in running container](/assets/Screenshot_20230223_031445.png)

* stop container by pressing `Ctrl + c`
* restart container with environment variable parameters `docker run --rm -p 4567:4567 -e FRONTEND_URL="*" -e BACKEND_URL="*" -it backend-flask:1.0`
* navigate to url in the **PORTS** tab in Gitpod, append `/api/activities/home` to url and json object will be visible in browser

![HINT: screenshot of browser json object from backend endpoint](/assets/Screenshot_20230223_031510.png)


### Get Images or Containers

`docker ps -a` displays running containers
`docker image ls -a` displays downloads images

### Send curl to Test Server
```bash
curl -X GET "http://localhost:4567/api/activities/home" -H "Accept: application/json" -H "Content-Type: application/json"
```

### Check Container logs
```bash
docker logs <CONTAINER_ID>
```
### Get Running Container ID to store in Environment Variable
`CONTAINER_ID=$(docker ps -q backend-flask:1.0)`

## Containerize Frontend

### Run NPM Install
We have to execute the `npm install` command before building the frontend container so that the needed dependencies are present 
```bash
cd frontend-react-js
npm i
```
### Create a Dockerfile
```bash
touch ./Dockerfile
```
Enter following code into `Dockerfile`:

```bash
FROM node:16.18

ENV PORT=3000

COPY . /frontend-react-js
WORKDIR /frontend-react-js
RUN npm install
EXPOSE ${PORT}
CMD ["npm", "start"]
```
### Build Container
```bash
cd ..
docker build -t frontend-reack-js:1.0 ./frontend-react-js
```

### Create docker-compose.yaml file
```bash
touch ./docker-compose.yml
```
add the following code into the `docker-compose.yml` file

```yml
version: "3.8"
services:
  backend-flask:
    environment:
      FRONTEND_URL: "http://3000-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
      BACKEND_URL: "http://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
    build: ./backend-flask
    ports:
      - "4567:4567"
    volumes:
       - ./backend-flask:/backend-flask
  frontend-react-js:
    environment:
      REACT_APP_BACKEND_URL: "http://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
    build: ./frontend-react-js
    ports:
      - "3000:3000"
    volumes:
       - ./frontend-react-js:/frontend-react-js
       
networks:
  internal-network:
    driver: bridge
    name: cruddur
```
- Right-click `docker-compose.yml` file and select **Docker Compose Up**
- Execute `docker ps` to view running containers for frontend and backend

![Hint screenshot of docker ps command showing containers running](/assets/Screenshot_20230223_043705.png)

- Ensure port 3000 & 4567 are unlocked/made public
- Click on url associated woth port 3000 to view front end of Cruddur app


![Screenshot of frontend of Cruddur app running in browser](/assets/Screenshot_20230223_044013.png)


### Create Notification Feature
#### Create and map backend endpoint
- In the `frontend-react-js` folder, execute this command `npm i`, if not completed earlier. 
- Then right-click the `docker-compose.yml` file and select **Docker Compose Up**
- Ensure ports 3000 and 4567 are open/unlocked in the **PORTS** tab
- Click on link associated with port 3000
- open the `backend-flask/openapi-3.0.yml` file in the Gitpod editor, then click on the `OpenAPI` extension in the left rail
- Click on the ellipsis and click **Add**
- in the new code snippet that was added to the file enter the following code:

```yaml
  /api/activities/notifications:
    get:
      description: 'Return a feed of all of those that I follow'
      tags:
        - activities
      parameters: []
      responses:
        '200':
          description: Returns array of activities
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Activity"
```
- create a `services/notifications_activities.py` file and insert the following code:

```python
from datetime import datetime, timedelta, timezone
class NotificationsActivities:
  def run():
    now = datetime.now(timezone.utc).astimezone()
    results = [{
      'uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
      'handle':  'Fifty_Pence',
      'message': 'Peep the game!',
      'created_at': (now - timedelta(days=2)).isoformat(),
      'expires_at': (now + timedelta(days=5)).isoformat(),
      'likes_count': 5,
      'replies_count': 1,
      'reposts_count': 0,
      'replies': [{
        'uuid': '26e12864-1c26-5c3a-9658-97a10f8fea67',
        'reply_to_activity_uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
        'handle':  'Worf',
        'message': 'This post has no honor!',
        'likes_count': 0,
        'replies_count': 0,
        'reposts_count': 0,
        'created_at': (now - timedelta(days=2)).isoformat()
      }],
    }
    ]
    return results
```
- append following code to `app.py` file

```yml

...
from services.notifications_activities import *
...


...
@app.route("/api/activities/notifications", methods=['GET'])
def data_notifications():
  data = NotificationsActivities.run()
  return data, 200
...
```

![HINT screenshot of 404 error to new backend endpoint]()
- Click on url associated with backend, port 4567 to view json object

![HINT screenshot of json object from new backend endpoint](/assets/Screenshot_20230223_155317.png)

#### Map new frontend endpoint to new backend endpoint
* append the frontend-react-js/src/App.js file with the following code:
```yml
import NotificationsFeedPage from './pages/NotificationsFeedPage';

...
  {
    path: "/notifications",
    element: <NotificationsFeedPage />
  },
```

* create `./frontend-react-js/src/pages/NotificationsFeedPage.js` & `./frontend-react-js/src/pages/NotificationsFeedPage.css` files
* copy contents from frontend-react-js/pages/HomeFeedPage.js to frontend-react-js/pages/NotificationsFeedPage.js & change references of home to notifications

![Hint screenshot of notifications page showing data from new backend endpoint]()

### DynamoDB Local & Postgres
#### DynamoDB
[AWS docs to run DynamoDB locally](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html)
- added Docker code to docker-compose.yml file to create DynamoDB container
- added root user to gain permission to read/write data

![HINT DynamoDB running locally](/assets/Screenshot_20230223_190630.png)

#### Postgres

add code snippet to `docker-compose.yml` file:

```yml
...
  db:
    image: postgres:13-alpine
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - '5432:5432'
    volumes: 
      - db:/var/lib/postgresql/data
...

  volumes:
    db:
      driver:local
```
added code snippet to implement healthcheck for database:

```yml
    healthcheck:
      test: ['CMD', 'pg_isready', '-U', 'postgres']
      interval: 1s
      timeout: 5s
      retries: 10
```

![HINT Postgres container running](/assets/Screenshot_20230223_203005.png)

