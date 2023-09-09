import logging
from os import environ

from telegram.ext import ApplicationBuilder

from handlers import HANDLERS

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = environ.get('BOT_TOKEN')

application = ApplicationBuilder().token(BOT_TOKEN).build()


def main():
    if not BOT_TOKEN:
        raise Exception('Missing bot token! Add the token to environment variable BOT_TOKEN')

    for handler in HANDLERS:
        application.add_handler(handler)

    application.run_polling()


if __name__ == '__main__':
    main()
