from os import environ

BOT_TOKEN = environ.get('BOT_TOKEN')

DB_USER = environ.get('DB_USER', 'bot')
DB_PASS = environ.get('DB_PASS', 'bot')
DB_HOST = environ.get('DB_HOST', 'localhost')
DB_PORT = environ.get('DB_PORT', '5432')
DB_NAME = environ.get('DB_NAME', 'bot')