from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes

from callbacks import help, start, stop, unknown, randomize, ignore, grade, register, present, timer, lesson
from log import logger

HANDLERS = (
    CommandHandler('help', help),
    CommandHandler('start', start),
    CommandHandler('stop', stop),
    CommandHandler('random', randomize),
    CommandHandler('ignore', ignore),
    CommandHandler('grade', grade),
    CommandHandler('register', register),
    CommandHandler('present', present),
    CommandHandler('timer', timer),
    CommandHandler('lesson', lesson),
    MessageHandler(filters.COMMAND, unknown)
)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log the error and send a message to the user."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if isinstance(update, Update):
        await update.message.reply_text("An error occurred, please try again later.")
