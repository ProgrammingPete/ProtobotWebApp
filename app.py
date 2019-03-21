"""
This is the script that will hold teh View, Models ,a nd the routes for the application.
THis will be changed in the future, if the code becomes to messy.

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
import api_tabulated_new
import _thread
import threading
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


import os
app = Flask(__name__)
cors = CORS(app, supports_credentials=True)

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


@app.route('/api/v1.0/update', methods=['GET'])
def get_tasks():
    return jsonify({'Trading_Info': api_tabulated_new.rawtable})


@app.route('/api/v1.0/success/<name>')
def success(name):
   return 'welcome %s' % name


@app.route('/api/v1.0/login', methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      userdata = request.get_json()
      user = userdata.get('email')
      password = userdata.get('password')
      if (authentication.validation(user, password)) == 1:
        return redirect('https://pbot2.azurewebsites.net/data') 
      else:
        return redirect('https://pbot2.azurewebsites.net/failure')


@app.route('/api/v1.0/create', methods = ['POST', 'GET'])
def create():
  if request.method == 'POST':
    userdata = request.get_json()
    user = userdata.get('email')
    password = userdata.get('password')
    if (authentication.createUser(user, password)) == 1:
        response = redirect('https://pbot2.azurewebsites.net/login')
        return response 
    else:
        return redirect('https://pbot2.azurewebsites.net/failure')


rawTab = threading.Thread(target= api_tabulated_new.rawtab, name = 'Table')
rawTab.start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5678')
