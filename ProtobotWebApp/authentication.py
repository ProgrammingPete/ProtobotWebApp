import os
import bcrypt
from app import User

credentialStorage= {}

def createUser(userName, password):
	salt = bcrypt.gensalt()
	hashValue = bcrypt.hashpw(password.encode('utf-8'), salt)
	credentialStorage[userName] = {'hashValue': hashValue, 'salt': salt}
	print(credentialStorage)
	print('length of hashval: ', len(credentialStorage[userName]['hashValue'].decode('utf-8')))
	print('length of salt: ', len(credentialStorage[userName]['salt'].decode('utf-8')))


def validation(username, password):
	compareValue = bcrypt.hashpw(password.encode('utf-8'), credentialStorage[username]['salt'])
	#Need to add section here to catch keyerrors i.e. the user does not exist
	if compareValue == credentialStorage[username]['hashValue']:
		return 1
	else:
		return 0