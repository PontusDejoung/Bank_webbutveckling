from dotenv import load_dotenv
import os

class ConfigDebug():
    load_dotenv(os.path.join(os.path.dirname(__file__), 'env', '.env'))
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('PASSWORD_SALT')
    REMEMBER_COOKIE_SAMESITE = 'strict'
    SESSION_COOKIE_SAMESITE = 'strict'
    MAIL_SERVER = 'sandbox.smtp.mailtrap.io'
    MAIL_PORT = 2525
    MAIL_USERNAME= os.getenv('MAIL_USER')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    SECURITY_FRESHNESS_GRACE_PERIOD = 1