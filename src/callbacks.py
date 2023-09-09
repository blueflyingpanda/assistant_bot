from telegram import Update
from telegram.ext import ContextTypes
from data import backed_data
from random import randint

from decorators import teacher_only, mutates_data


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):

    help_text = """/help -- displays main features of the bot

/start -- the one who starts the bot is considered a teacher and has higher privileges 

/stop -- only teacher can stop the bot

/present name1 name2 -- will increase the presence count for listed students by one.
Name1 1
Name2 3

/grade +- name1 name2 -- rule's 1st argument is an option + (for prepared students) or - (for unprepared students)
Name1 ++
Name2
Name3 -

/random -- saves you the trouble of choosing who will go to the blackboard
Name2

/ignore name0 -- useful if chat has someone else apart from teacher and students
ignored: name0, name4

/add name0 -- add students, removes them from ignored if necessary
students: name0, name1, name2, name3
ignored: name4

/timer N -- sets the timer for N minutes
Timer set for 5 minutes
…
Times up!
"""

    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)


@mutates_data
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if teacher := backed_data.data.get('teacher'):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Current teacher is {teacher}')
    else:
        backed_data.data['teacher'] = update.effective_user.name
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"New teacher is {backed_data.data['teacher']}"
        )


@teacher_only
@mutates_data
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    backed_data.data.clear()
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Bot was stopped')


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I didn't understand that command")


async def randomize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    students = backed_data.data.get('students')
    if not students:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='No students registered yet')
    else:
        # TODO: shuffle instead of randint
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"I've chosen {list(students)[randint(0, len(students) - 1)]}"
        )


@teacher_only
@mutates_data
async def ignore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    students = backed_data.data.get('students', {})
    outsiders = backed_data.data.get('outsiders', [])

    for candidate in context.args:
        if candidate in students:
            students.pop(candidate)
            outsiders.append(candidate)

    backed_data.data['outsiders'] = outsiders
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Ignored: {", ".join(outsiders)}')


@teacher_only
@mutates_data
async def present(update: Update, context: ContextTypes.DEFAULT_TYPE):
    students = backed_data.data.get('students', {})
    for candidate in context.args:
        if candidate not in students:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=f'No such student {candidate}. Skipping ...'
            )
            continue

        students[candidate]['attendance'] += 1

    response = '\n'.join([f'{student} {metrics["attendance"]}' for student, metrics in students.items()])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


@teacher_only
@mutates_data
async def grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed_grades = ('+', '-')
    students = backed_data.data.get('students', {})

    if len(context.args) < 1 or context.args[0] not in allowed_grades:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Grade +/- not specified')
    else:
        is_positive = context.args[0] == '+'

        for candidate in context.args[1:]:
            if candidate not in students:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, text=f'No such student {candidate}. Skipping ...'
                )
                continue

            students[candidate]['points'] += 1 if is_positive else -1

    stats = []
    for student, metrics in students.items():
        if metrics["points"] > 0:
            mark = '+' * metrics["points"]
        else:
            mark = '-' * -metrics["points"]
        stats.append(f'{student} {mark}')

    response = '\n'.join(sorted(stats))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)


@teacher_only
@mutates_data
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    students = backed_data.data.get('students', {})
    new_students = set(context.args) - set(students)
    students.update({student: {'points': 0, 'attendance': 0} for student in new_students})

    backed_data.data['students'] = students
    backed_data.data['outsiders'] = list(
        set(backed_data.data.get('outsiders', [])) - set(list(backed_data.data['students']))
    )
