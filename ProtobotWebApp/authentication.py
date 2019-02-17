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
    newUser = User(username = userName, hashvalue = hashValue.decode('utf-8'), password_salt = salt.decode('utf-8'))
    db.session.add(newUser)
    db.session.commit()

def validation(username, password):
	compareValue = bcrypt.hashpw(password.encode('utf-8'), credentialStorage[username]['salt'])
	#Need to add section here to catch keyerrors i.e. the user does not exist
	if compareValue == credentialStorage[username]['hashValue']:
		return 1
	else:
		return 0