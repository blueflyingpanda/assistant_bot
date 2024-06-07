from datetime import date
from functools import partial
from random import randint

from telegram import Update
from telegram.ext import ContextTypes, CallbackContext

from data import DataStorage, UserInfo, PARTICIPATION_TYPES
from decorators import teacher_only
from exceptions import LogicError, NotFoundError
from log import logger
from bot import Bot


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """/help -- displays main features of the bot

/start -- the one who starts the bot is considered a teacher and has higher privileges 

/stop -- only teacher can stop the bot

/present name1 name2 -- will increase the presence count for listed students by one.
Name1 1
Name2 3

/grade <+- or 0-10> name1 name2 -- rule's 1st argument is an option + (for prepared students) or - (for unprepared students)
Name1 ++
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

/lesson title -- begins a lesson
"""

    # TODO: /stats /add_teacher
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_title = chat.title
    chat_id = chat.id

    if not chat_title:
        return await update.message.reply_text('This chat does not have a title.')

    # TODO: many groups in one chat
    group_title, _, course_title = chat_title.partition(' ')

    if not (group_title and course_title):
        return await update.message.reply_text('Wrong chat title! Should follow the pattern <group> <course>.')

    tg_user = update.effective_user
    user_info = UserInfo(f'{tg_user.id}', tg_user.username, tg_user.full_name)

    ds = DataStorage(chat_id)

    exists, course_info = ds.get_or_create_course(
        user_info=user_info, title=course_title, group=group_title
    )

    if exists:
        invite_link = await context.bot.export_chat_invite_link(chat_id)
        return await update.message.reply_text(
            text=f'Course already exists: {invite_link}'
        )

    course = course_info.course
    teacher = course_info.teachers[0]

    await update.message.reply_text(
        'Chat created successfully.\n'
        f'Course: {course.title}\n'
        f'Year: {course.year}\n'
        f'Group: {course.group}\n'
        f'Teacher: {teacher.name}'
    )


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Bot cannot be stopped 👹\n'
             'Kick it from the chat.'
    )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if msg := update.effective_message.text:
        logger.warning(msg)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I didn't understand that command")


async def randomize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    ds = DataStorage(chat_id)

    students = ds.get_presented()
    if not students:
        await Bot.display_no_students(update, context)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"I've chosen {students[randint(0, len(students) - 1)]}"
        )


@teacher_only
async def ignore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if len(candidates := context.args) != 1:
        return await context.bot.send_message(chat_id=chat_id, text='Please specify one student')
    try:
        ds = DataStorage(chat_id)
        ds.remove_student(candidates[0].lstrip('@'))

    except NotFoundError as e:
        msg = f'{chat_id}: {e.__doc__}'
        logger.warning(msg)
        return await context.bot.send_message(
            chat_id=chat_id, text=f'{e.__doc__}'
        )

    except LogicError as e:
        msg = f'{chat_id}: {e.args[0]}'
        logger.warning(msg)
        return await context.bot.send_message(chat_id=chat_id, text=e.args[0])

    await context.bot.send_message(chat_id=chat_id,
                                   text=f'Specified user is no longer considered a student. '
                                        f'/register to make them student again')


@teacher_only
async def present(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    candidates = {candidate.lstrip('@') for candidate in context.args}  # removing @ from username

    if not candidates:
        return await context.bot.send_message(chat_id=chat_id, text='Please specify present students')

    ds = DataStorage(chat_id)
    try:
        skipped = ds.mark_present(candidates)
        if skipped:
            await context.bot.send_message(
                chat_id=chat_id, text=f'Skipped: {", ".join(skipped)}'
            )
    except NotFoundError as e:
        msg = f'{chat_id}: {e.__doc__}'
        logger.warning(msg)
        return await context.bot.send_message(
            chat_id=chat_id, text='Lesson should be started before checking attendance. Press /lesson'
        )

    attendances = ds.get_attendance()
    await Bot.display_attendance(attendances, update, context)


@teacher_only
async def grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    common_marks = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'}
    bonus_marks = set(PARTICIPATION_TYPES.keys())
    allowed_marks = common_marks | bonus_marks

    candidates = {candidate.lstrip('@') for candidate in context.args[1:]}
    ds = DataStorage(chat_id)

    if len(context.args) < 1 or ((mark := context.args[0]) not in allowed_marks):
        return await context.bot.send_message(chat_id=update.effective_chat.id, text='Grade not specified')

    display_func = Bot.display_participation
    get_performance = ds.get_performance

    if mark.isdigit():
        mark = int(mark)
        display_func = Bot.display_grades
        get_performance = partial(get_performance, fetch_grades=True)

    try:
        skipped = ds.grade_students(candidates, mark)
    except NotFoundError as e:
        msg = f'{chat_id}: {e.__doc__}'
        logger.warning(msg)
        return await context.bot.send_message(
            chat_id=chat_id, text='Lesson should be started before grading students. Press /lesson'
        )

    if skipped:
        await context.bot.send_message(
            chat_id=chat_id, text=f'Skipped: {", ".join(skipped)}'
        )

    performance_by_student = get_performance()
    await display_func(performance_by_student, update, context)


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    tg_user = update.effective_user
    user_id = f'{tg_user.id}'

    ds = DataStorage(chat_id)
    user_info = UserInfo(user_id, tg_user.username, tg_user.full_name)

    try:
        ds.add_student(user_info)
    except LogicError as e:
        msg = f'{chat_id}: {e.args[0]}'
        logger.warning(msg)
        return await context.bot.send_message(chat_id=chat_id, text=e.args[0])
    except NotFoundError as e:
        msg = f'{chat_id}: {e.__doc__}'
        logger.warning(msg)
        return await context.bot.send_message(chat_id=chat_id, text='Teacher should start the bot first')

    await context.bot.send_message(
        chat_id=chat_id, text=f'student {tg_user.full_name or tg_user.username} registered'
    )


async def timer(update: Update, context: CallbackContext):
    async def timer_callback(_context: CallbackContext):
        await _context.bot.send_message(chat_id=_context.job.chat_id, text="Time's up!")

    minutes = 0
    max_minutes = 1440
    if context.args and context.args[0].isdigit() and minutes <= max_minutes:
        minutes = int(context.args[0])
    await update.message.reply_text(f'Timer started for {minutes} minutes.')

    context.job_queue.run_once(timer_callback, minutes * 60, chat_id=update.message.chat_id)


@teacher_only
async def lesson(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    title = ' '.join(context.args)
    ds = DataStorage(chat_id)
    ds.start_lesson(title, date.today())

    message = await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Started lesson {title}')
    await context.bot.pin_chat_message(chat_id=chat_id, message_id=message.message_id)
