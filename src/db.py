import asyncio
from datetime import date

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import mapped_column, Mapped, relationship, DeclarativeBase

from conf import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
from log import ALCHEMY_ECHO


DESCRIBE = False


class Base(DeclarativeBase, AsyncAttrs):
    """Base model"""


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
    tg_id: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str]

    attendances: Mapped[list['Attendance']] = relationship(back_populates='user')
    courses: Mapped[list['UserCourseAssociation']] = relationship(back_populates='user')


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint('title', 'group', name='uq_title_year_group'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[str] = mapped_column(unique=True, index=True)
    title: Mapped[str]
    year: Mapped[int]
    exam_weight: Mapped[int | None] = mapped_column(comment='exam weight in percent', default=40)
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
    participation: Mapped[bool | None]

    user: Mapped['User'] = relationship(back_populates='attendances')
    lesson: Mapped['Lesson'] = relationship(back_populates='attendances')


async_engine = create_async_engine(
    f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}', echo=ALCHEMY_ECHO
)
ASession = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)


async def main():
    if DESCRIBE:
        from sqlalchemy.sql.ddl import CreateTable
        from sqlalchemy.dialects.postgresql import dialect
        for table in Base.metadata.sorted_tables:
            create_table_sql = f'{(CreateTable(table).compile(dialect=dialect()))}'
            print(create_table_sql)
    else:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    asyncio.run(main())
