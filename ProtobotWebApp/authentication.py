import os
import bcrypt

credentialStorage= {}

def createUser(userName, password):
	salt = bcrypt.gensalt()
	hashValue = bcrypt.hashpw(password.encode('utf-8'), salt)
	credentialStorage[userName] = {'hash': hashValue, 'salt': salt}



def createPassword(password):
	salt = bcrypt.gensalt()
	hashValue = bcrypt.hashpw(password.encode('utf-8'), salt)



def validation(username, password):
	compareValue = bcrypt.hashpw(password.encode('utf-8'), credentialStorage[username][salt])

	if compareValue == hashValue:
		print(compareValue)
		print("Password Verified")

	else:
		print("Wrong Password")