'''Settings module'''
import os

DB_URI = os.environ.get('DB_CONNECT')
TELEGRAM_API_KEY = os.environ.get('API_KEY')
DEFAULT_LOCALE = os.environ.get('DEFAULT_LOCALE')
LOCALIZATION_PATH = os.environ.get('LOCALIZATION_PATH')
USER_SECRETS_MAX = os.environ.get('USER_SECRETS_MAX', 150)
SECRET_HASH_LENGTH = os.environ.get('SECRET_HASH_LENGTH', 30)
