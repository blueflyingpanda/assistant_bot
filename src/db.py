from datetime import date

from sqlalchemy import create_engine, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, mapped_column, Mapped, relationship, sessionmaker

from log import ALCHEMY_ECHO

Base = declarative_base()


class UserCourseAssociation(Base):
    """intermediate table for users related to courses"""

    __tablename__ = "users_courses"

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'), primary_key=True)

    teacher: Mapped[bool] = mapped_column(default=False)

    user: Mapped['User'] = relationship(back_populates='courses')
    course: Mapped['Course'] = relationship(back_populates='users')


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str | None]
    name: Mapped[str | None]

    attendances: Mapped[list['Attendance']] = relationship(back_populates='user')
    courses: Mapped[list['UserCourseAssociation']] = relationship(back_populates='user')


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint('title', 'year', 'group', name='uq_title_year_group'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    year: Mapped[int]
    exam_weight: Mapped[int | None] = mapped_column(comment='exam weight in percent', default=40)
    tg_link: Mapped[str] = mapped_column(unique=True)
    group: Mapped[str]

    lessons: Mapped[list['Lesson']] = relationship(back_populates='course')
    users: Mapped[list['UserCourseAssociation']] = relationship(back_populates='course')


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    type: Mapped[int] = mapped_column(comment='0-lecture 1-lab 2-seminar')
    date: Mapped[date]
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))

    course: Mapped['Course'] = relationship(back_populates='lessons')
    attendances: Mapped[list['Attendance']] = relationship(back_populates='lesson')


class Attendance(Base):
    __tablename__ = "attendances"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    lesson_id: Mapped[int] = mapped_column(ForeignKey('lessons.id'))
    grade: Mapped[int | None]
    participation: Mapped[bool] = mapped_column(default=False)

    user: Mapped['User'] = relationship(back_populates='attendances')
    lesson: Mapped['Lesson'] = relationship(back_populates='attendances')


engine = create_engine('postgresql://bot:bot@localhost:5432/bot', echo=ALCHEMY_ECHO)
Session = sessionmaker(bind=engine)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
