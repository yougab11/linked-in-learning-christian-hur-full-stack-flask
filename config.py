import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'\xd1\xb3k{8BI\x9d"\\\xc8\xf2\x85\xad\x8d\xa7'

    MONGODB_SETTINGS = { 'db' : 'uta_db' }