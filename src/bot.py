from collections import defaultdict

from telegram import Update
from telegram.ext import ContextTypes


class Bot:
    """Representation Layer"""

    @classmethod
    async def display_attendance(cls, students_info: dict[str, int], update: Update, context: ContextTypes.DEFAULT_TYPE):
        response = '\n'.join(sorted([f'{username} {attendance}' for username, attendance in students_info.items()]))
        if response:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        else:
            await cls.display_no_students(update, context)

    @classmethod
    async def display_participation(cls, students_info: dict[str, list[bool]], update: Update, context: ContextTypes.DEFAULT_TYPE):
        stats = []

        for name, info in students_info.items():
            points = info.count(True) - info.count(False)
            if points > 0:
                mark = '+' * points
            else:
                mark = '-' * -points
            stats.append(f'{name}: {mark}')

        response = '\n'.join(sorted(stats))

        if response:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        else:
            await cls.display_no_students(update, context)

    @classmethod
    async def display_grades(cls, students_info: dict[str, list[int]], update: Update, context: ContextTypes.DEFAULT_TYPE):
        stats = []

        for name, info in students_info.items():
            stats.append(f'{name}: {", ".join(map(str, filter(lambda val: val is not None, info)))}')

        response = '\n'.join(sorted(stats))

        if response:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
        else:
            await cls.display_no_students(update, context)

    @classmethod
    async def display_no_students(cls, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text='No students present yet')