"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""

from flask import Flask, jsonify, redirect, url_for, request, render_template
import api_tabulated_new
import _thread
import threading
app = Flask(__name__)
import authentication

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

@app.route('/')
def hello():
    """Renders a sample page."""
    return render_template('login.html')

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
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5678'))
    except ValueError:
        PORT = 5555
    rawTab = threading.Thread(target= api_tabulated_new.rawtab, name = 'Table')
    rawTab.start()
    app.run(HOST, 5678, debug = True)