# Week 2 — Distributed Tracing
## Configure Cruddur to send data to Honeycomb.io
[Honeycomb.io OpenTelemetry docs using Python](https://docs.honeycomb.io/getting-data-in/opentelemetry/python/)
- install the following Python packages and append to `backend-flask/requirements.txt`

```
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp-proto-http
opentelemetry-instrumentation-flask
opentelemetry-instrumentation-requests
```
- make updates to `backend-flask/app.py`
- setup environment variable for Honeycomb access key

`export HONEYCOMB_API_KEY="HONEYCOMB_API_KEY"`

```python
# app.py updates
    
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter


# Honeycomb ----
# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())

# Show this in the logs within backend-flask app
simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Initialize automatic instrumentation with Flask
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
```
### Configure OpenTelemetry by setting environment variables

```sh
export HONEYCOMB_API_KEY="Honeycomb API key goes here" 
```
- update `docker-compose.yml` file 

```yaml
services:
  backend-flask:
    environment:
      OTEL_SERVICE_NAME: "backend-flask"
      OTEL_EXPORTER_OTLP_ENDPOINT: "https://api.honeycomb.io"
      OTEL_EXPORTER_OTLP_HEADERS: "x-honeycomb-team=${HONEYCOMB_API_KEY}"
```
- run frontend and backend containers by running docker compose up on the `docker-compose.yml` file

```docker compose -f "docker-compose.yml" up -d --build```

### Acquire a tracer and create a span
- append `backend-flask/services/home_activities.py`
- insert sample code from [docs.honeycomb.io](https://docs.honeycomb.io/getting-data-in/opentelemetry/python/#configure-and-run) into the class method, run()

```python
# Honeycomb --------
from opentelemetry import trace


tracer = trace.get_tracer("home.activities")

class HomeActivities:
    def run():
        with tracer.start_as_current_span("home-activities-mock-data") as inner_span:
            span = trace.get_current_span()
            now = datetime.now(timezone.utc).astimezone()
            span.set_attribute("app.now", now.isoformat())
            results = [{
                'uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',

            ...
            ]
            span = trace.get_current_span()
            span.set_attribute("app.result_length", len(results))
            return results
```
-  navigate to BACKEND_URL/api/activities/home several times to send data to Honeycomb API endpoint
-  navigate to [Honeycomb UI](https://ui.honeycomb.io) and click on **Home** tab to view spans
![HINT show visuals of spans from Honeycomb.io](https://user-images.githubusercontent.com/85846263/222890369-55301a98-539f-43d8-a129-0e09dc260967.png)

### Query Honeycomb.io database engine
- heatmap, P90, count

## CloudWatch Logs
- insert **watchtower** in the `backend-flask/requirements.txt` file
- install requirements by executing `python3 -m pip install -r requirements.txt`
- update `backend-flask/app.py`

```python
...
--- CloudWatch ---
import watchtower
import logging
from time import strftime


Configuring Logger to use CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
cw_handler = watchtower.CloudWatchLogHandler(log_group="cruddur")
logger.addHandler(console_handler)
logger.addHandler(cw_handler)
logger.info("test log")
...

@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error(f"{timestamp} {request.remote_addr} {request.method} {request.scheme} {request.full_path} {response.status}")
    return response
  
@app.route("/api/activities/home", methods=['GET'])
def data_home():
    data = HomeActivities.run(logger=logger)
    return data, 200
    ...
```
- append the `backend-flask/services/home_activities.py` file

```python
...
class HomeActivities:
    def run(logger):
        logger.info("HomeActivities")
            with tracer.start_as_current_span("home-activities-mock-data") as inner_span:
                span = trace.get_current_span()
                ...
```
- append the `docker-compose.yml` file

```yaml
services:
  backend-flask:
    environment:
...

      AWS_DEFAULT_REGION: "${AWS_DEFAULT_REGION}"
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
```
- navigate to `BACKEND_URL/api/activities/home`, then login to AWS Management Console and navigate to **CloudWatch** > **Log groups** > **cruddur** to view log files

![HINT pics of CloudWatch Log Group created & displaying logs](/assets/Screenshot_20230228_021434.png)

## Instrument XRay
- append `backend-flask/requirements.txt` with **aws-xray-sdk**
- install requirements by executing `python3 -m pip install -r requirements.txt`
- update `backend-flask/app.py`

```python
...
---- AWS XRay ----
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.ext.flask.middleware import XRayMiddleware
...

xray_url = os.getenv("AWS_XRAY_URL")
xray_recorder.configure(service="backend-flask", dynamic_naming=xray_url)
XRayMiddleware(app, xray_recorder)

...
```
- create a `aws/json/xray.json` file with the following contents:

```json
{
  "SamplingRule": {
    "RuleName": "Cruddur",
    "ResourcesARN": "*",
    "Priority": 9000,
    "FixedRate": 0.1,
    "ResevoirSize": 5,
    "ServiceName": "backend-flask",
    "ServiceType": "*",
    "Host": "*",
    "HTTPMethod": "*",
    "URLPath": "*",
    "Version": 1
  }
}
```
- create an XRay group via the AWS CLI

```sh
aws xray create-group --group-name "Cruddur" --filter-expression "service(\"backend-flask\")"
```
![](/assets/Screenshot_20230301_002522.png)

- add XRay daemon and related environment variables to `docker-compose.yml`

```yml
service:
  backend-flask:
    environment:
      AWS_XRAY_URL: "*4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
      AWS_XRAY_DAEMON_ADDRESS: "xray-daemon:2000"
...
  xray-daemon:
    image: "amazon/aws-xray-daemon"
    environment:
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
      AWS_REGION: "${AWS_DEFAULT_REGION}"
    command:
      - "xray --local-mode --bind xray-daemon:2000"
    ports:
      - 2000:2000/udp
```
- create a sampling rule via AWS CLI

```sh
aws xray create-sampling-rule --cli-json-output file://aws/json/xray.json
```
![](/assets/Screenshot_20230301_020936.png)
- Navigate to `BACKEND_URL/api/activities/home` & check the logs of the backend-flask container to see data generated by XRay

![HINT backend-flask logs displaying data generated by XRay](/assets/Screenshot_20230303_142056.png)

- navigate to **CloudWatch > XRay > Traces**
![HINT XRay data displayed on CloudWatch Traces](/assets/Screenshot_20230303_141808.png)

## Configure Rollbar
- append `backend-flask/requirements.txt` with **blinker & rollbar**
- install requirements by executing `python3 -m pip install -r requirements.txt`
- navigate to rollbar.com, login and retrieve access token
- setup Rollbar access token as a environment variable in the terminal

```sh
export ROLLBAR_ACCESS_TOKEN="ROLLBAR_ACCESS_TOKEN"
```
- update `backend-flask/app.py` with necessary import statements and Rollbar initialization
```python
...
# --- Rollbar ---
import rollbar
import rollbar.contrib.flask
from flask import got_request_exception

...

# insert below app = Flask(__name__)
# --- Rollbar ---
rollbar_access_token = os.getenv('ROLLBAR_ACCESS_TOKEN')

@app.before_first_request
def init_rollbar():
    """init rollbar module"""
    rollbar.init(
        # access token
        rollbar_access_token,
        # environment name
        'development',
        # server root directory, makes tracebacks prettier
        root=os.path.dirname(os.path.realpath(__file__)),
        # flask already sets up logging
        allow_logging_basic_config=False)

    # send exceptions from `app` to rollbar, using flask's signal system.
    got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

#  --- Rollbar ---
@app.route('/rollbar/test')
def rollbar_test():
    rollbar.report_message("Hello World!", "warning")
    return "Hello World!"
```
- add environment variable to `docker-compose.yml` file
```yaml
services:
  backend-flask:
    environment:
      ROLLBAR_ACCESS_TOKEN: "${ROLLBAR_ACCESS_TOKEN}"
```
- execute `docker compose -f "docker-compose.yml" up -d --build` to run containers
- check to see if ports are open to public/unlocked
- navigate to `BACKEND_URL/rollbar/test` to see Hello World! page, this will confirm that rollbar was correctly configured

![HINT of Hello World! pic](/assets/Screenshot_20230304_012918.png)

- then navigate to [Rollbar](https://rollbar.com) > Dashboard > select all levels to display collected data in dashboard

![HINT pic of rollbar data dashboard](/assets/Screenshot_20230304_013309.png)
