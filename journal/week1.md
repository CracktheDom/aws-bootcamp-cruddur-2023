# Week 1 — App Containerization

## VSCode Docker Extension
Docker for VSCode makes it easy to use Docker

| Gitpod comes preinstalled with extension

## Containerizer Backend

### Run Python

```sh
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

```bash
docker build -t backend-flask:1.0 ./backend-flask
```

### Run Container

```bash
some command
```

