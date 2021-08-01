'''
This file can be used to read credentials that a stored in a 
hidden credentials folder on your private networ drive
'''
import os

def get_credentials(app):
    cred = None
    target = 'credentials\\'
    
    for f in os.listdir(target):
        if app in f:
            data = open(target+f, 'r').readlines()
            cred = {}
            cred['u'] = data[0].strip()
            cred['p'] = data[1].strip()
            break
            
    return cred