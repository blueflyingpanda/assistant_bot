from os import environ

# BOT_TOKEN = '7437435023:AAHUBkyGI1ugHd5tHSSxKUsyP4m-uJF8pY8'
BOT_TOKEN = environ.get('BOT_TOKEN', '7437435023:AAHUBkyGI1ugHd5tHSSxKUsyP4m-uJF8pY8')
# BOT_TOKEN = environ.get('TELEGRAM_BOT_TOKEN')

DB_USER = environ.get('DB_USER', 'postgres')
DB_PASS = environ.get('DB_PASS', 'root')
DB_HOST = environ.get('DB_HOST', 'localhost')
DB_PORT = environ.get('DB_PORT', '5432')
DB_NAME = environ.get('DB_NAME', 'postgres')

