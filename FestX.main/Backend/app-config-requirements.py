# config.py
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-development-only'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fest_management.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# requirements.txt
flask==2.3.3
flask-sqlalchemy==3.0.5
flask-login==0.6.2
flask-wtf==1.1.1
email-validator==2.0.0
flask-migrate==4.0.4
werkzeug==2.3.7
python-dotenv==1.0.0
itsdangerous==2.1.2
pillow==10.0.0
