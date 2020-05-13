from flask import Flask, jsonify, redirect, url_for, request, render_template, send_file
import ProtobotWebApp.api_tabulated_new as api
from ProtobotWebApp.prerendr import update_panels
from ProtobotWebApp.make_celery import make_celery
import _thread
import threading
import os

#cors issues. This is is only a temporary fix.
#from flask_cors import CORS

app = Flask(__name__)

app.config.from_object(__name__)
app.config.update(dict(
    JSONIFY_PRETTYPRINT_REGULAR=False
))
app.config.from_envvar('FLASK_SERVER_SETTINGS', silent=True)

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)

celery = make_celery(app)
#CORS(app)

#db stuff
from ProtobotWebApp.mariaDB import db_session
from ProtobotWebApp.models import User



basedir = os.path.abspath(os.path.dirname(__file__))


from  ProtobotWebApp.authentication import validation, createUser

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


@app.teardown_appcontext
def shutdown_dbsession(exception=None):
    db_session.remove()

## route example: /api/v1.0/update?pair=<STRING HERE>
## for now, can only be BTCUSDT or ETHUSDT
@app.route('/api/v1.0/update', methods=['GET'])
def get_tasks():
    pair = request.args.get('pair', type = str, default = 'BTCUSDT')
    if pair in api.supported_pairs:
        return jsonify({'Trading_Info': api.supported_pairs[pair]})
    else:
        return jsonify({'Error' : 'unsupported'})

# route example: /api/v1.0/historical?start=<STRING HERE>?end=<STRING HERE>
#params can be in any order, but you have to include start param
#try to define the strings as dates (Open_Time): 2019/04/10 14:40:00
@app.route('/api/v1.0/historical')
def historical():
    start = request.args.get('start', type = str)
    end = request.args.get('end', type = str, default = 'now')
    interval = request.args.get('interval', default = '1m', type = str)
    trading_pair = request.args.get('pair', default = 'BTCUSDT', type = str)
    # igotta make sure that end is ALWAYS after start
    if start and start[-2:] == '00': #make sure start exists and seconds are 00  
        data = api.get_historical(start, end,  interval, trading_pair)
        return jsonify({'historical' : data })
    else:
        return jsonify('failure, invalid start or start not included')


@app.route('/api/v1.0/btcOneMonth')
def btcOneMonth():
    try:
        return send_file('prerendered/preBTCUSDT30.csv', attachment_filename='preBTCUSDT30.csv')
    except Exception as e:
        return str(e)


@app.route('/api/v1.0/ethOneMonth')
def ethOneMonth():
    try:
        return send_file('prerendered/preETHUSDT30.csv', attachment_filename='preETHUSDT30.csv')
    except Exception as e:
        return str(e)


@app.route('/api/v1.0/btcOneWeek')
def btcOneWeek():
    try:
        return send_file('prerendered/preBTCUSDT30.csv', attachment_filename='preBTCUSDT30.csv')
    except Exception as e:
        return str(e)


@app.route('/api/v1.0/ethOneWeek')
def ethOneWeek():
    try:
        return send_file('prerendered/preETHUSDT7.csv', attachment_filename='preETHUSDT7.csv')
    except Exception as e:
        return str(e)


@app.route('/api/v1.0/btcOneDay')
def btcOneDay():
    try:
        return send_file('prerendered/preBTCUSDT1.csv', attachment_filename='preBTCUSDT1.csv')
    except Exception as e:
        return str(e)


@app.route('/api/v1.0/ethOneDay')
def ethOneDay():
    try:
        return send_file('prerendered/preETHUSDT1.csv', attachment_filename='preETHUSDT1.csv')
    except Exception as e:
        return str(e)


@app.route('/api/v1.0/login', methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      userdata = request.get_json()
      user = userdata.get('email')
      password = userdata.get('password')
      if (validation(user, password)) == 1:
        response = 'success'
        return jsonify(response)
      else:
        response = 'failure'
        return jsonify(response)


@app.route('/api/v1.0/create', methods = ['POST', 'GET'])
def create():
  if request.method == 'POST':
    userdata = request.get_json()
    user = userdata.get('email')
    password = userdata.get('password')
    if (createUser(user, password)) == 1:
        response = 'success'
        return jsonify(response)
    else:
        response = 'failure'
        return jsonify(response)
