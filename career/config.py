import os
from datetime import timedelta

class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    BROADCAST_KEY='TechnicalNomad'

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    