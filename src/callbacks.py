from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from data import backed_data
from random import randint
from utils import display_students_attendance, get_username, display_no_students

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

/ignore name0 -- specified users are no longer considered students

/register every student presses this button
student name0 registered

/timer N -- sets the timer for N minutes
Timer set for 5 minutes
…
Times up!
"""

    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)


@mutates_data
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if teacher_id := backed_data.data.get('teacher'):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Current teacher is {await get_username(teacher_id, context)}'
        )
    else:
        backed_data.data['teacher'] = update.effective_user.id
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=f"New teacher is {update.effective_user.name}"
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
        await display_no_students(update, context)
    else:
        # TODO: shuffle instead of randint
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"I've chosen {[student['name'] for student in students.values()][randint(0, len(students) - 1)]}"
        )


@teacher_only
@mutates_data
async def ignore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    students = backed_data.data.get('students', {})

    name_to_id = {
        info['name']: student_id for student_id, info in students.items()
    }

    for candidate in context.args:
        if candidate in name_to_id:
            students.pop(name_to_id[candidate])

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f'Specified users are no longer considered students. '
                                        f'/register to make them students again '
                                        f'but their progress is lost')


@teacher_only
@mutates_data
async def present(update: Update, context: ContextTypes.DEFAULT_TYPE):
    students = backed_data.data.get('students', {})

    name_to_info = {
        info['name']: {'attendance': info['attendance'], 'id': student_id} for student_id, info in students.items()
    }

    for candidate in context.args:
        if candidate not in name_to_info:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=f'No such student {candidate}. Skipping ...'
            )
            continue

        student = students[name_to_info[candidate]['id']]
        student['attendance'] += 1
        name_to_info[candidate]['attendance'] = student['attendance']  # will be used later to display information

    await display_students_attendance(name_to_info, update, context)


@teacher_only
@mutates_data
async def grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed_grades = ('+', '-')
    students = backed_data.data.get('students', {})

    name_to_info = {
        info['name']: {'points': info['points'], 'id': student_id} for student_id, info in students.items()
    }

    if len(context.args) < 1 or context.args[0] not in allowed_grades:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Grade +/- not specified')
    else:
        is_positive = context.args[0] == '+'

        for candidate in context.args[1:]:
            if candidate not in name_to_info:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, text=f'No such student {candidate}. Skipping ...'
                )
                continue
            student = students[name_to_info[candidate]['id']]
            student['points'] += 1 if is_positive else -1
            name_to_info[candidate]['points'] = student['points']  # will be used later to display information

    stats = []
    for name, info in name_to_info.items():
        points = info['points']
        if points > 0:
            mark = '+' * points
        else:
            mark = '-' * -points
        stats.append(f'{name} {mark}')

    response = '\n'.join(sorted(stats))

    if response:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    else:
        await display_no_students(update, context)


@mutates_data
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if teacher := backed_data.data.get('teacher'):
        if int(teacher) == update.effective_user.id:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text='Teacher cannot be registered as student'
            )
        else:
            students = backed_data.data.get('students', {})
            student_id = f'{update.effective_user.id}'

            if student_id not in students:
                students[student_id] = {'points': 0, 'attendance': 0, 'name': update.effective_user.name}
            else:
                # if user changed the username
                students[student_id]['name'] = update.effective_user.name

            backed_data.data['students'] = students
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=f'student {update.effective_user.name} registered'
            )
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Teacher should start the bot first')


async def timer(update: Update, context: CallbackContext):
    async def timer_callback(_context: CallbackContext):
        await _context.bot.send_message(chat_id=_context.job.chat_id, text="Time's up!")

    minutes = 0
    max_minutes = 1440
    if context.args and context.args[0].isdigit() and minutes <= max_minutes:
        minutes = int(context.args[0])
    await update.message.reply_text(f'Timer started for {minutes} minutes.')

    context.job_queue.run_once(timer_callback, minutes * 60, chat_id=update.message.chat_id)
