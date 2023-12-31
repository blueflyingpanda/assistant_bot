from telegram import Update
from telegram.ext import ContextTypes

from data import backed_data


def teacher_only(func):
    async def decorated(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if teacher_id := backed_data.data.get('teacher'):
            if teacher_id == update.effective_user.id:
                await func(update, context)
            else:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, text=f'Only teacher can perform this action'
                )
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Press /start to be a teacher')

    return decorated


def mutates_data(func):
    async def decorated(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await func(update, context)
        backed_data.save()

    return decorated
