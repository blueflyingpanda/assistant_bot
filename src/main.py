from os import environ

from telegram.ext import ApplicationBuilder

from handlers import HANDLERS

BOT_TOKEN = environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise Exception('Missing bot token! Add the token to environment variable BOT_TOKEN')

application = ApplicationBuilder().token(BOT_TOKEN).build()
for handler in HANDLERS:
    application.add_handler(handler)


def main():
    application.run_polling()


if __name__ == '__main__':
    main()
