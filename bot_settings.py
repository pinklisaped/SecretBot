'''Settings module'''
import os

DB_URI = os.environ['DB_CONNECT']
TELEGRAM_API_KEY = os.environ['API_KEY']
DEFAULT_LOCALE = os.environ['DEFAULT_LOCALE']
LOCALIZATION_PATH = os.environ.get('LOCALIZATION_PATH')
USER_SECRETS_MAX = os.environ.get('USER_SECRETS_MAX', 150)
SECRET_HASH_LENGTH = os.environ.get('SECRET_HASH_LENGTH', 30)
