import logging
from os import environ

from telegram import Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler

from handlers import HANDLERS

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = environ.get('BOT_TOKEN')

application = ApplicationBuilder().token(BOT_TOKEN).build()


async def timer_callback(context: CallbackContext):
    await context.bot.send_message(context.job.chat_id, "Time's up!")


async def timer(update: Update, context: CallbackContext):
    minutes = 1
    MAX_MINUTES = 1440
    if context.args and context.args[0].isdigit() and minutes <= MAX_MINUTES:
        minutes = int(context.args[0])
    await update.message.reply_text(f'Timer started for {minutes} minutes.')

    application.job_queue.run_once(timer_callback, minutes * 60, chat_id=update.message.chat_id)


def main():
    if not BOT_TOKEN:
        raise Exception('Missing bot token! Add the token to environment variable BOT_TOKEN')

    application.add_handler(CommandHandler('timer', timer))

    for handler in HANDLERS:
        application.add_handler(handler)

    application.run_polling()


if __name__ == '__main__':
    main()
