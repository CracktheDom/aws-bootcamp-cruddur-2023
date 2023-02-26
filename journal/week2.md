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

# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
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
