# Week 1 — App Containerization

## VSCode Docker Extension
Docker for VSCode makes it easy to use Docker

| Gitpod comes preinstalled with extension

## Containerize Backend

### Run Python

```bash
cd backend-flask
export FRONTEND_URL="*"
export BACKEND_URL="*"
python -m flask run --host=0.0.0.0 --port=4567
```
- make sure port 4567 is open/unlocked via Gitpod **PORTS** tab
- click on url in **PORTS** tab
- and append /api/activities/home to url
- should see json object in browser

![HINT input url for json response]()

### Add Dockerfile

Create a file here: `backend-flask/Dockerfile`
Input the following into file:

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

* stop Flask server with Ctrl + c
* execute the following commands in the terminal:
```bash
unset FRONTEND_URL
unset BACKEND_URL
cd ..
docker build -t backend-flask:1.0 ./backend-flask
```

execute `docker image ls` to confirm that image was created

![Hint screenshot of docker image command]()

### Run Container

```bash
docker run --rm -p 4567:4567 -it backend-flask:1.0
```
* ensure port 4567 is unlocked in **PORTS** tab in Gitpod
* navigate to url displayed in **PORTS**
* should see **404 Not Found** page and the server running in terminal should confirm this by displaying the same error code
* stop container and run again with env
* execute `docker ps` to view running containers with ID
* execute `docker logs <container id>` to views logs running container
* **OR** in Docker extension right-click on running container and click on `Attach Shell` to execute commands within the container
* within container execute `env | grep _URL` to verify syntax of above was incorrect and did not pass env to container
* `docker run --rm -p 4567:4567 -e FRONTEND_URL="*" -e BACKEND_URL="*" -it backend-flask:1.0`
* navigate to url in **PORTS** tab in Gitpod, append /api/activities/home to url and json object will be present

### Get Images or Containers

```bash
docker ps -a
docker image ls
```

### Send curl to Test Server
```bash
curl -X GET http://localhost:4567/api/activities/home -H "Accept: application/json" -H Content-Type: application/json"
```

### Check Container logs
```bash
docker logs <CONTAINER_ID>
```
### Get Container ID to store in Environment variable
CONTAINER_ID=$(docker run --rm -p 4567:4567 -d backend-flask:1.0)

## Containerize Frontend

### Run NPM Install
We have to execute the `npm install` command before building the container so that the contents of node_modules will be copied
```bash
cd frontend-react-js
npm i
```
### Create a Dockerfile
```bash
touch /frontend-react-js/Dockerfile
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
docker build -t frontend-reack-js:1.0 ./frontend-react-js
```

### Create docker-compose.yaml file
```bash
touch /docker-compose.yml
```
add the following code into the `docker-compose.yml` file

```yml
version: "3.8"
services:
  backend-flask:
    environment:
      FRONTEND_URL: "http://3001-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
      BACKEND_URL: "http://4567-${GITPOS_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
    build: ./backend-flask
    ports:
      - "4567:4567"
     volumes:
       - ./backend-flask:/backend-flask
  frontend-react-js:
    environment:
      REACT_APP_BACKEND_URL: "http://4567-${GITPOS_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST})"
    build: ./frontend-react-js
    ports:
      - "3000:3000"
    volumes:
       - ./frontend-flask:/frontend-flask
       
networks:
  internal-network:
    driver: bridge
    name: cruddur
```
