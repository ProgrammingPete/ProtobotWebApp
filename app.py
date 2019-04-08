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

from flask import Flask, jsonify, redirect, url_for, request, render_template
import api_tabulated_new as api
import _thread
import threading
from flask_sqlalchemy import SQLAlchemy

import os

app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
#configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #signals the app every time a change is made to db
db = SQLAlchemy(app)

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


@app.route('/api/v1.0/success/<name>')
def success(name):
   return 'welcome %s' % name

# route example: /api/v1.0/historical?end=<STRING HERE>?start=<STRING HERE>
@app.route('/api/v1.0/historical')
def historical():
    end = request.args.get('end', type = str)
    start = request.args.get('start', default = 'now', type = str)
    interval = request.args.get('interval', default = '1m', type = str)
    trading_pair = request.args.get('pair', default = 'BTCUSDT', type = str)
    data = api_tabulated_new.get_historical(end, start, interval, trading_pair)
    return jsonify({'historical' : data }) 

@app.route('/api/v1.0/login', methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      userdata = request.get_json()
      user = userdata.get('email')
      password = userdata.get('password')
      if (authentication.validation(user, password)) == 1:
        response = redirect('https://pbot.azurewebsites.net', code=301)
        return response
      else:
        response = redirect('https://pbot.azurewebsites.net/failure', code=301)
        return response


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
    for t in api.supported_pairs.keys():
        tab = threading.Thread(target= api.rawtab, name = str(t) + ' Thread', kwargs = {'filename': 'rawtab_' + str(t) + '.csv','pair' : t})
        tab.start()
    
