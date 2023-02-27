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
- configure opentelemetry by setting environment variables

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

```python
from opentelemetry import trace

...

tracer = trace.get_tracer("home_activities")

class HomeActivities():
    with tracer.start_as_current_span("home_activities_mock_data") as inner_span:
        inner_span.set_attribute("inner", True)

    ...

    span = trace.get_current_span()
    span.set_attribute("user.id", user.id())


```
-  
