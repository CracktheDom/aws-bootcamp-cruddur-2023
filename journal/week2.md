# Week 2 — Distributed Tracing
## Configure Cruddur to send data to Honeycomb.io
!(https://docs.honeycomb.io/getting-data-in/opentelemetry/python/)
- install the following Python packages

```
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp-proto-http
opentelemetry-instrumentation-flask
opentelemetry-instrumentation-requests
```
- make updates to app.py

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
### configure opentelemetry by setting environment variables

```sh
export HONEYCOMB_API_KEY="Honeycomb API key goes here" 
```
- update docker-compose.yml file 

```yaml
services:
    backend-flask:
        environment:
            OTEL_SERVICE_NAME: "backend-flask"
            OTEL_EXPORTER_OTLP_ENDPOINT: "https://api.honeycomb.io"
            OTEL_EXPORTER_OTLP_HEADERS: "x-honeycomb-team=${HONEYCOMB_API_KEY}"
```
- run frontend and backend containers by running docker compose up on the docker-compose.yml file
- navigate to backend /api/activites/home and /api/activites/notificaations endpoint to generate date to send to Honeycomb API endpoint
- go to Honeycomb.io UI to dataset

![HINT show visuals of spans from Honeycomb.io]

### Acquire a tracer and create a span
- append backend-flask/services/home_activities.py
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
-  navigate to ui.honeycomb.io and click on **Home** tab to view spans

### Query Honeycomb.io database engine
- heatmap, P90, count

## CloudWatch Logs
- insert watchtower in the `backend-flask/requirements.txt` file to install watchtower
- update backend/app.py

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
- update `backend-flask/services/home_activities.py`

```python
...
class HomeActivities:
  def run(logger):
    logger.info("HomeActivities")
      with tracer.start_as_current_span("home-activities-mock-data") as inner_span:
        span = trace.get_current_span()
...
```
- update `docker-compose.yml`

```yaml
services:
    backend-flask:
        environment:
...

      AWS_DEFAULT_REGION: "${AWS_DEFAULT_REGION}"
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
```
- navigate to BACKEND_URL/api/activities/home, then login to AWS Management Console and navigate to **CloudWatch** > **Log groups** > **cruddur** to log files

![HINT pics of CloudWatch Log Group created & displaying logs]()

## Instrument XRay
- append backend-flask/requirements.txt with aws-xray-sdk
- update app.py

```python
...
---- AWS XRay ----
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.ext.flask.middleware import XRayMiddleware
...

xray_url = os.getenv("AWS_XRAY_URL")
xray_recorder.configure(service="backend-flask", dynamic_naming=xray_url)
XRayMiddleware = (app, xray_recorder)

...
```
- create a aws/json/xray.json file with the following contents:

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

```bash
aws xray create-group --group-name "Cruddur" --filter-expression "service(\"backend-flask\")"
```
