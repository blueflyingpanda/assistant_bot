from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from sqlalchemy import select, func

from db import User, Course, ASession, UserCourseAssociation, Lesson, Attendance
from exceptions import LogicError, CourseNotFoundError, StudentNotFoundError, LessonNotFoundError
from log import logger


LESSON_TYPES = {
    'lecture': 0,
    'lab': 1,
    'seminar': 2,
}


PARTICIPATION_TYPES = {
    '+': True,
    '-': False
}


@dataclass
class UserInfo:
    id: str
    username: str
    full_name: str


@dataclass
class CourseInfo:
    students: list[User]
    teachers: list[User]
    course: Course


class DataStorage:
    """
    Data Access Layer
    NB: protected methods don't open session so that they could be used within one session
    """

    def __init__(self, chat_id: int):
        self.chat_id: str = f'{chat_id}'
        self.course_related_subquery = (
                select(UserCourseAssociation.user_id)
                .join(Course, Course.id == UserCourseAssociation.course_id)
                .where(Course.chat_id == self.chat_id)
                .subquery()
            )

    async def _get_course(self, session: ASession, loud: bool = False) -> CourseInfo | None:
        result = await session.execute(
            select(Course).where(Course.chat_id == self.chat_id)
        )
        course = result.scalars().first()

        if not course:
            if loud:
                raise CourseNotFoundError()

            return None

        stmt = select(UserCourseAssociation).where(UserCourseAssociation.course_id == course.id)
        result = await session.execute(stmt)

        students = []
        teachers = []

        for association in result.scalars().all():
            if association.teacher:
                teachers.append(await association.awaitable_attrs.user)
            else:
                students.append(await association.awaitable_attrs.user)

        return CourseInfo(students, teachers, course)

    async def get_course(self) -> CourseInfo | None:
        async with ASession() as session:
            return await self._get_course(session)

    async def get_or_create_course(self, user_info: UserInfo, title: str, group: str) -> tuple[bool, CourseInfo]:
        """:return: pair where first element is True if course exists, else False"""

        async with ASession() as session:
            course_info = await self._get_course(session)
            exists = course_info is not None

            if not exists:
                course = Course(
                    chat_id=self.chat_id,
                    title=title,
                    group=group,
                    year=date.today().year,
                )

                result = await session.execute(
                    select(User).where(User.tg_id == user_info.id)
                )
                teacher = result.scalars().first()

                if not teacher:
                    teacher = User(
                        tg_id=user_info.id,
                        username=user_info.username,
                        name=user_info.full_name
                    )

                # link the user and the course, indicating that the user is a teacher
                assoc = UserCourseAssociation(teacher=True)
                assoc.user = teacher

                course.users.append(assoc)

                session.add_all((course, teacher, assoc))
                await session.commit()

                course_info = CourseInfo(students=[], teachers=[teacher], course=course)

            return exists, course_info

    async def _get_user(self, session: ASession, tg_id: str, loud: bool = False) -> User | None:
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        student = result.scalars().first()

        if not student and loud:
            raise StudentNotFoundError()

        return student

    async def _bind_student_with_course(self, session: ASession, student: User, course: Course):
        # link the user and the course, indicating that the user is a student
        assoc = UserCourseAssociation(teacher=False)
        assoc.user = student

        (await course.awaitable_attrs.users).append(assoc)

        session.add_all((course, student, assoc))

    async def add_student(self, user_info: UserInfo):
        async with ASession() as session:
            course_info = await self._get_course(session)

            if not course_info:
                raise CourseNotFoundError()

            student = await self._get_user(session, user_info.id)

            students_tg_ids = {st.tg_id for st in course_info.students}
            teachers_tg_ids = {teacher.tg_id for teacher in course_info.teachers}

            if not student:
                if not user_info.username or not user_info.full_name:
                    raise LogicError('Cannot add student without username or full name')

                student = User(
                    tg_id=user_info.id,
                    username=user_info.username,
                    name=user_info.full_name
                )
            else:
                if student.tg_id in teachers_tg_ids:
                    raise LogicError('Teacher cannot be registered as student')
                # update student info
                logger.warning(f'User {user_info} update attempt')
                student.username = user_info.username
                student.name = user_info.full_name

            if student.tg_id not in students_tg_ids:
                await self._bind_student_with_course(session, student, course_info.course)

            session.add(student)
            await session.commit()

    async def check_is_teacher(self, tg_user_id: str) -> bool:
        async with ASession() as session:
            course_info = await self._get_course(session, loud=True)

            teachers_tg_ids = {t.tg_id for t in course_info.teachers}

            return tg_user_id in teachers_tg_ids

    async def start_lesson(self, title: str, dt: date):
        async with ASession() as session:
            course_info = await self._get_course(session, loud=True)
            lesson = Lesson(
                title=title,
                type=LESSON_TYPES['lab'],  # TODO add other types
                date=dt,
                course_id=course_info.course.id
            )

            session.add(lesson)
            await session.commit()

    async def mark_present(self, candidates: set[str]) -> list[str]:
        """marks students as present and returns skipped candidates"""
        async with ASession() as session:
            course_info = await self._get_course(session, loud=True)

            course = course_info.course

            if not await course.awaitable_attrs.lessons:
                raise LessonNotFoundError()

            presented = set(await self._get_presented(session))
            by_usernames = {st.username: st for st in course_info.students}
            skipped: list[str] = []
            attendances: list[Attendance] = []

            for candidate in candidates:
                if (student := by_usernames.get(candidate)) and candidate not in presented:
                    attendances.append(Attendance(
                        user_id=student.id,
                        lesson_id=course.lessons[-1].id
                    ))
                else:
                    skipped.append(candidate)

            session.add_all(attendances)
            await session.commit()

            return skipped

    async def grade_students(self, candidates: set[str], mark: int | str) -> list[str]:
        async with ASession() as session:
            course_info = await self._get_course(session, loud=True)

            course = course_info.course

            if not await course.awaitable_attrs.lessons:
                raise LessonNotFoundError()

            skipped: list[str] = []
            performances: list[Attendance] = []

            stmt = (
                select(User.username, Attendance)
                .join(User, Attendance.user_id == User.id)
                .join(UserCourseAssociation, UserCourseAssociation.user_id == User.id)
                .where(Attendance.lesson_id == course.lessons[-1].id)
                .where(User.username.in_(candidates))
                .where(UserCourseAssociation.course_id == course.id)
            )

            result = await session.execute(stmt)
            result = result.all()

            # Execute the query
            attendance_by_username: dict[str, Attendance] = dict(result)

            for candidate in candidates:
                if attendance := attendance_by_username.get(candidate):
                    if (participation := PARTICIPATION_TYPES.get(mark)) is not None:
                        attendance.participation = participation
                    else:
                        attendance.grade = mark
                    performances.append(attendance)
                else:
                    skipped.append(candidate)

            session.add_all(performances)
            await session.commit()

            return skipped

    async def get_attendance(self) -> dict[str, int]:
        """returns usernames to amount of lessons they attended"""

        async with ASession() as session:
            stmt = (
                select(User.username, func.count(Attendance.id).label('attendance_count'))
                .join(Attendance, Attendance.user_id == User.id)
                .join(Lesson, Attendance.lesson_id == Lesson.id)
                .join(Course, Course.id == Lesson.course_id)
                .where(Course.chat_id == self.chat_id)
                .where(User.id.in_(select(self.course_related_subquery.c.user_id)))
                .group_by(User.username)
            )

            result = await session.execute(stmt)
            attendances = result.all()

            return dict(attendances)

    async def get_performance(self, fetch_grades: bool = False) -> dict[str, list[int | bool]]:
        async with ASession() as session:
            stmt = (
                select(User.username, Attendance.grade if fetch_grades else Attendance.participation)
                .join(Attendance, Attendance.user_id == User.id)
                .join(Lesson, Attendance.lesson_id == Lesson.id)
                .join(Course, Course.id == Lesson.course_id)
                .where(Course.chat_id == self.chat_id)
                .where(User.id.in_(select(self.course_related_subquery.c.user_id)))
            )

            result = await session.execute(stmt)
            performances = result.all()

            performance_by_student = defaultdict(list)

            for username, participation in performances:
                performance_by_student[username].append(participation)

            return performance_by_student

    async def _get_presented(self, session: ASession) -> list[str]:
        latest_lesson_date_subquery = (
            select(func.max(Lesson.id))
            .join(Course, Course.id == Lesson.course_id)
            .where(Course.chat_id == self.chat_id)
        ).scalar_subquery()

        stmt = (
            select(User.username)
            .join(Attendance, Attendance.user_id == User.id)
            .join(Lesson, Attendance.lesson_id == Lesson.id)
            .join(Course, Course.id == Lesson.course_id)
            .where(Course.chat_id == self.chat_id)
            .where(Lesson.id == latest_lesson_date_subquery)
            .where(User.id.in_(select(self.course_related_subquery.c.user_id)))
        )

        result = await session.execute(stmt)
        presented = result.scalars().all()
        return presented

    async def get_presented(self) -> list[str]:
        async with ASession() as session:
            return await self._get_presented(session)

    async def remove_student(self, username: str):
        async with ASession() as session:
            result = await session.execute(
                select(User).filter(User.username == username)
            )
            user = result.scalars().first()

            if not user:
                raise StudentNotFoundError()
            course_info = await self._get_course(session, loud=True)

            course = course_info.course
            result = await session.execute(
                select(UserCourseAssociation)
                .where(UserCourseAssociation.user_id == user.id)
                .where(UserCourseAssociation.course_id == course.id)
                .where(UserCourseAssociation.teacher.is_(False))
            )
            user_course_assoc = result.scalars().one_or_none()

            if not user_course_assoc:
                raise LogicError('User is not related to course as student')

            await session.delete(user_course_assoc)
            await session.commit()
