import os
import bcrypt
from app import User
from app import db

credentialStorage= {}

def createUser(userName, password):
    salt = bcrypt.gensalt()
    hashValue = bcrypt.hashpw(password.encode('utf-8'), salt)
    credentialStorage[userName] = {'hashValue': hashValue, 'salt': salt}

    #add to database
    newUser = User(username = userName, hashvalue = hashValue, password_salt = salt)
    db.session.add(newUser)
    db.session.commit()

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