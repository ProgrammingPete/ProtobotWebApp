import os
import bcrypt
import sqlalchemy

from ProtobotWebApp.models import User
from ProtobotWebApp.mariaDB import db_session

credentialStorage= {}

def createUser(userName, password):
    salt = bcrypt.gensalt()
    hashValue = bcrypt.hashpw(password.encode('utf-8'), salt)
    credentialStorage[userName] = {'hashValue': hashValue, 'salt': salt}
    try:
        #add to database
        newUser = User(username = userName, hashvalue = hashValue, password_salt = salt)
        db_session.add_all([newUser])
        db_session.commit()
        print("User added to the database")
        return 1
    except sqlalchemy.exc.IntegrityError as e:
        print("Error when writing to DB" + e)
        return 0

def validation(username, password):
    try:
        currentuser = User.query.filter_by(username = username).first()
        compareValue = bcrypt.hashpw(password.encode('utf-8'), currentuser.password_salt)
        if compareValue == currentuser.hashvalue:
            return 1
        else:
            return 0
    except AttributeError:
        return 0
