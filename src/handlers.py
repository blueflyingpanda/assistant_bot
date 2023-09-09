from telegram.ext import CommandHandler, MessageHandler, filters

from callbacks import help, start, stop, unknown, randomize, ignore, grade, add, present, timer

HANDLERS = (
    CommandHandler('help', help),
    CommandHandler('start', start),
    CommandHandler('stop', stop),
    CommandHandler('random', randomize),
    CommandHandler('ignore', ignore),
    CommandHandler('grade', grade),
    CommandHandler('add', add),
    CommandHandler('present', present),
    CommandHandler('timer', timer),
    MessageHandler(filters.COMMAND, unknown)
)
