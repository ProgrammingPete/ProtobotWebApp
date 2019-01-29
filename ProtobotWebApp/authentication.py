import os
import bcrypt
salt = bcrypt.gensalt()
password = 'Tony is the best'

hashValue = bcrypt.hashpw(password.encode('utf-8'), salt)
print(salt)
print(hashValue)