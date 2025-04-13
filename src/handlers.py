from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes

from assistant_bot.src.callbacks import help, start, stop, unknown, randomize, ignore, grade, register, present, timer, lesson
from logs import custom_logger

HANDLERS = (
    CommandHandler('help', help, block=False),
    CommandHandler('start', start, block=False),
    CommandHandler('stop', stop, block=False),
    CommandHandler('random', randomize, block=False),
    CommandHandler('ignore', ignore, block=False),
    CommandHandler('grade', grade, block=False),
    CommandHandler('register', register, block=False),
    CommandHandler('present', present, block=False),
    CommandHandler('timer', timer, block=False),
    CommandHandler('lesson', lesson, block=False),
    MessageHandler(filters.COMMAND, unknown, block=False)
)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log the error and send a message to the user."""
    custom_logger.error(msg='Exception while handling an update:', exc_info=context.error)

    if isinstance(update, Update):
        await update.message.reply_text("An error occurred, please try again later.")

