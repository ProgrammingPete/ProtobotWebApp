import os
import bcrypt
salt = bcrypt.gensalt()
password = 'testing'
print("whats is your name?: ")
name = input()

hashValue = bcrypt.hashpw(password.encode('utf-8'), salt)
print(salt)
print(hashValue)

storage = {'Name': name, 'Hash': hashValue, 'Salt': salt}

print("What is your password?: ")
passwdInput = input()

compareValue = bcrypt.hashpw(passwdInput.encode('utf-8'), salt)

if compareValue == hashValue:
	print(compareValue)
	print("Password Verified")

else:
	print("Wrong Password")
