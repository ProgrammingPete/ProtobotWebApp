import os
import bcrypt

credentialStorage= {}

def createUser(userName, password):
	salt = bcrypt.gensalt()
	hashValue = bcrypt.hashpw(password.encode('utf-8'), salt)
	credentialStorage[userName] = {'hashValue': hashValue, 'salt': salt}


def validation(username, password):
	compareValue = bcrypt.hashpw(password.encode('utf-8'), credentialStorage[username]['salt'])

	if compareValue == credentialStorage[username]['hashValue']:
		return 1
	else:
		return 0