from telegram.ext import ApplicationBuilder

from conf import BOT_TOKEN
from handlers import HANDLERS, error_handler


if not BOT_TOKEN:
    raise Exception('Missing bot token! Add the token to environment variable BOT_TOKEN')

application = ApplicationBuilder().token(BOT_TOKEN).build()

application.add_handlers(HANDLERS)
application.add_error_handler(error_handler)


def main():
    application.run_polling()


if __name__ == '__main__':
    main()
