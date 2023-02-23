# Week 1 — App Containerization

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

Create a file here: backend-flask/Dockerfile
