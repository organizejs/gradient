class BaseConfig:
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_CONFIRMABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_REGISTERABLE = False # so we can specify our own registration route
    SECURITY_POST_LOGIN_VIEW = '/home'
