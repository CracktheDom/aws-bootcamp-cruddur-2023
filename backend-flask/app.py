import os
from flask import Flask, request, got_request_exception
from flask_cors import CORS, cross_origin

from services.home_activities import HomeActivities
from services.notifications_activities import NotificationsActivities
from services.user_activities import UserActivities
from services.create_activity import CreateActivity
from services.create_reply import CreateReply
from services.search_activities import SearchActivities
from services.message_groups import MessageGroups
from services.messages import Messages
from services.create_message import CreateMessage
from services.show_activity import ShowActivities

# Honeycomb -------
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

# ---- AWS XRay ----
# from aws_xray_sdk.core import xray_recorder
# from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

# --- CloudWatch ---
# import watchtower
# import logging
# from time import strftime

# --- Rollbar ---
import rollbar
import rollbar.contrib.flask

# ---FlaskAWSCognito JWT service ---
from lib.cognitoJWTVerification import TokenService, TokenVerifyError


# Configuring Logger to use CloudWatch
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# console_handler = logging.StreamHandler()
# cw_handler = watchtower.CloudWatchLogHandler(log_group="cruddur")
# logger.addHandler(console_handler)
# logger.addHandler(cw_handler)
# logger.info("test log")

# Honeycomb ----
# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)

# Show this in the logs within backend-flask app
simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(simple_processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Initialize automatic instrumentation with Flask
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)  # Honeycomb
RequestsInstrumentor().instrument()  # Honeycomb
frontend = os.getenv('FRONTEND_URL')
backend = os.getenv('BACKEND_URL')
origins = [frontend, backend]
cors = CORS(
  app, 
  resources={r"/api/*": {"origins": origins}},
  headers=["Content-Type", "Authorization"],
  expose_headers="location,link,Authorization",
  allow_headers="content-type,if-modified-since",
  methods="OPTIONS,GET,HEAD,POST"
)

# ---- XRay ----
# xray_url = os.getenv("AWS_XRAY_URL")
# xray_recorder.configure(service="backend-flask", dynamic_naming=xray_url)
# XRayMiddleware(app, xray_recorder)

# ---- CloudWatch ----
# @app.after_request
# def after_request(response):
#   timestamp = strftime('[%Y-%b-%d %H:%M]')
#   logger.error(f"{timestamp} {request.remote_addr} {request.method} {request.scheme} {request.full_path} {response.status}")
#   return response


# ---FlaskAWSCognito JWT service ---
cognitoTokenService = TokenService(
  user_pool_id=os.getenv("AWS_COGNITO_USER_POOL_ID"), 
  user_pool_client_id=os.getenv("AWS_COGNITO_USER_POOL_CLIENT_ID"), 
  region=os.getenv("AWS_DEFAULT_REGION")
)

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

    # # extra fields we'd like to send along to rollbar (optional)
    # extra_data = {'datacenter': 'us1', 'app' : {'version': '0.1'}}
    
    # # report full exception info
    # rollbar.report_exc_info(sys.exc_info(), request, extra_data=extra_data)

    # # and/or, just send a string message with a level
    # rollbar.report_message("Here's a message", 'info', request, extra_data=extra_data)

    # yield '<p>Caught an exception</p>'
    return "Hello World!"

  
@app.route("/api/message_groups", methods=['GET'])
def data_message_groups():
  user_handle  = 'andrewbrown'
  model = MessageGroups.run(user_handle=user_handle)
  if model['errors'] is not None:
    return model['errors'], 422
  return model['data'], 200


@app.route("/api/messages/@<string:handle>", methods=['GET'])
def data_messages(handle):
  user_sender_handle = 'andrewbrown'
  user_receiver_handle = request.args.get('user_reciever_handle')

  model = Messages.run(
    user_sender_handle=user_sender_handle, 
    user_receiver_handle=user_receiver_handle
    )
  if model['errors'] is not None:
    return model['errors'], 422
  return model['data'], 200


@app.route("/api/messages", methods=['POST','OPTIONS'])
@cross_origin()
def data_create_message():
  user_sender_handle = 'andrewbrown'
  user_receiver_handle = request.json['user_receiver_handle']
  message = request.json['message']

  model = CreateMessage.run(
    message=message,
    user_sender_handle=user_sender_handle,
    user_receiver_handle=user_receiver_handle
    )
  if model['errors'] is not None:
    return model['errors'], 422
  return model['data'], 200


@app.route("/api/activities/home", methods=['GET'])
@cross_origin()
def data_home():
  access_token = cognitoTokenService.extract_access_token(request.headers)  
  try:
    cognitoTokenService.verify(access_token)
  except TokenVerifyError as e:
    _ = request.data
    abort(make_response(jsonify(message=str(e)), 401))

  # app.logger.debug('claims')
  # app.logger.debug(cognitoTokenService.claims)
  data = HomeActivities.run()  # enter logger=logger as a parameter to enable logging to CloudWatch
  return data, 200


@app.route("/api/activities/notifications", methods=['GET'])
@cross_origin()
def data_notifications():
  data = NotificationsActivities.run()
  return data, 200


@app.route("/api/activities/@<string:handle>", methods=['GET'])
def data_handle(handle):
  model = UserActivities.run(handle)
  if model['errors'] is not None:
    return model['errors'], 422
  return model['data'], 200

@app.route("/api/activities/search", methods=['GET'])
def data_search():
  term = request.args.get('term')
  model = SearchActivities.run(term)
  if model['errors'] is not None:
    return model['errors'], 422
  return model['data'], 200


@app.route("/api/activities", methods=['POST','OPTIONS'])
@cross_origin()
def data_activities():
  user_handle  = 'andrewbrown'
  message = request.json['message']
  ttl = request.json['ttl']
  model = CreateActivity.run(message, user_handle, ttl)
  if model['errors'] is not None:
    return model['errors'], 422
  return model['data'], 200


@app.route("/api/activities/<string:activity_uuid>", methods=['GET'])
def data_show_activity(activity_uuid):
  data = ShowActivities.run(activity_uuid=activity_uuid)
  return data, 200


@app.route("/api/activities/<string:activity_uuid>/reply", methods=['POST','OPTIONS'])
@cross_origin()
def data_activities_reply(activity_uuid):
  user_handle  = 'andrewbrown'
  message = request.json['message']
  model = CreateReply.run(message, user_handle, activity_uuid)
  if model['errors'] is not None:
    return model['errors'], 422
  return model['data'], 200

if __name__ == "__main__":
  app.run(debug=True)
