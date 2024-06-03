from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from log import logger


async def display_students_attendance(students_info: dict, update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = '\n'.join([f'{name} {info["attendance"]}' for name, info in students_info.items()])
    if response:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    else:
        await display_no_students(update, context)


async def get_username(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    username = None
    try:
        chat = await context.bot.get_chat(user_id)
        username = f'@{chat.username}'
    except Exception as e:
        logger.warning(f'{e}')
    return username


async def display_no_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='No students registered yet')
