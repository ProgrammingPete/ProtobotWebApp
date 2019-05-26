"""
This is the script that will hold the Models and Routes for the application.
This will be changed in the future, if the code becomes to messy.

How to use the database: 
If you change the schema, you will need to update the db file in a python shell:
    from app import db
    from app import User
    db.drop_all()
    db.create_all()

    Make a query:
        User.query
"""

from flask import Flask, jsonify, redirect, url_for, request, render_template, send_file
import api_tabulated_new as api
from prerendr import update_panels
import _thread
import threading
from flask_sqlalchemy import SQLAlchemy
from werkzeug.contrib.cache import MemcachedCache
import os

#cors issues. This is is only a temporary fix.
from flask_cors import CORS

app = Flask(__name__)

CORS(app)



basedir = os.path.abspath(os.path.dirname(__file__))
#configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #signals the app every time a change is made to db
db = SQLAlchemy(app)

#cache = MemcachedCache(['127.0.0.1:11211'])

class User(db.Model):
    """Class representation of a Client"""
    username = db.Column(db.String(120),  unique = True, primary_key = True, nullable= False)
    hashvalue = db.Column(db.String(61),  nullable = False) #60 byte hash
    password_salt = db.Column(db.String(30), nullable = False) # 29 byte salt

    def __repr__(self): #tells how python should represent the object
        return '<User {}>'.format(self.username)

import authentication

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

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
#       print(end, start)
#       e = end.replace(' ', '')
#       s = start.replace(' ', '')
#       if end == 'now':
#           data = cache.get('historical:' + s)
#       else:
#           data = cache.get('historical:' + s + ',' + e)
#       print(e, s)
#       if data is None:
#           print('no cache')
#           data = api.get_historical(start, end,  interval, trading_pair)
#           if end == 'now':
#               cache.set('historical:' + s, data, timeout=60)
#           else:
#               cache.set('historical:' + s + ',' +  e, data, timeout=360)
#       else:
#           print('using cache')
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
       #f  = cache.get('btcOneWeek')
       #if f is None:
       #    f = send_file('prerendered/preBTCUSDT7.csv', attachment_filename='preBTCUSDT7.csv')
       #    print(f)
       #    cache.set('btcOneWeek', f, timeout=360)
       #    print('cached the file')
       #else:
       #    print('retreived from cached')
       #return f 
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
      if (authentication.validation(user, password)) == 1:
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
    if (authentication.createUser(user, password)) == 1:
        response = 'success'
        return jsonify(response)
    else:
        response = 'failure'
        return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5678')
else:
    #needed to place threads here to avoid duplicate threads for some crap reason
    #i need to get rid of multithreading and go with multiprocessing for prod 
    for t in api.supported_pairs.keys():
        tab = threading.Thread(target= api.rawtab, name = str(t) + ' Thread', kwargs = {'filename': 'rawtab_' + str(t) + '.csv','pair' : t})
        tab.start()
    
