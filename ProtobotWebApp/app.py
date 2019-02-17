"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, jsonify, redirect, url_for, request, render_template
import api_tabulated_new
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

@app.route('/')
def hello():
    """Renders a sample page."""
    return render_template('login.html')

@app.route('/createUser')
def CreateUser():
    return render_template('createUser.html')

@app.route('/api/v1.0/update', methods=['GET'])
def get_tasks():
    return jsonify({'Trading Info': api_tabulated_new.rawtable})

@app.route('/api/v1.0/success/<name>')
def success(name):
   return 'welcome %s' % name

@app.route('/api/v1.0/login', methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      user = request.form['user_name']
      password = request.form['user_password']

      if (authentication.validation(user, password)) == 1:
        return ('%s Login Successful' %user) 
      else:
        return ('Login Unsuccesful, Please try again')
   else:
      return 'fail'

@app.route('/api/v1.0/create', methods = ['POST', 'GET'])
def create():
  if request.method == 'POST':
    user = request.form['user_name']
    password = request.form['user_password']
    authentication.createUser(user, password)
    return ('%s User Created' %user)
  else:
    return 'fail'

if __name__ == '__main__':   
    HOST = os.environ.get('SERVER_HOST', 'localhost')

    rawTab = threading.Thread(target= api_tabulated_new.rawtab, name = 'Table')
    rawTab.start()
    app.run(HOST, 5678, debug = True)