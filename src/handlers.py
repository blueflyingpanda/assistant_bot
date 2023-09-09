from telegram.ext import CommandHandler, MessageHandler, filters

from callbacks import help, start, stop, unknown, randomize, ignore, grade, add

HANDLERS = (
    CommandHandler('help', help),
    CommandHandler('start', start),
    CommandHandler('stop', stop),
    CommandHandler('random', randomize),
    CommandHandler('ignore', ignore),
    CommandHandler('grade', grade),
    CommandHandler('add', add),
    MessageHandler(filters.COMMAND, unknown)
)
