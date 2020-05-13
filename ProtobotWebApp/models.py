from sqlalchemy import Column, Integer, String
from ProtobotWebApp.mariaDB import Base



class User(Base):
    """Class representation of a Client"""
    __tablename__ = 'users'
    
    username = Column(String(120),  unique = True, primary_key = True, nullable= False)
    hashvalue = Column(String(61),  nullable = False) #60 byte hash
    password_salt = Column(String(30), nullable = False) # 29 byte salt
    
    def __init__(self, username=None, hashvalue=None, password_salt=None):
            self.username = username
            self.hashvalue = hashvalue
            self.password_salt = password_salt
            
    def __repr__(self): #tells how python should represent the object
        return '<User {}, hash: {}, salt: {} >'.format(self.username, self.hashvalue, self.password_salt )