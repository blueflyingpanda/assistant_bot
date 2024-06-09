from telegram import Update
from telegram.ext import ContextTypes

from data import DataStorage
from exceptions import NotFoundError
from logs import custom_logger


def teacher_only(func):
    """Basic role model restriction"""
    async def decorated(update: Update, context: ContextTypes.DEFAULT_TYPE):

        chat_id = update.effective_chat.id
        tg_user_id = f'{update.effective_user.id}'

        ds = DataStorage(chat_id)
        try:
            is_teacher = await ds.check_is_teacher(tg_user_id)
        except NotFoundError as e:
            msg = f'{chat_id}: {e.__doc__}'
            custom_logger.warning(msg)
            return await context.bot.send_message(chat_id=chat_id, text='Teacher should start the bot first')

        if is_teacher:
            await func(update, context)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'Only teacher can perform this action. If you are a teacher, press /start'
            )

    return decorated
