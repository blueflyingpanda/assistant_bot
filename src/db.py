from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    year = Column(Integer, nullable=False)


class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    year = Column(Integer)
    teachers = Column(Integer)
    exam_weight = Column(Integer)

class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    type = Column(Integer)
    date = Column(Date)
    course_id = Column(Integer, ForeignKey('courses.id'))
    course = relationship("Course", back_populates="lessons")


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=False)
    name = Column(String)
    phone = Column(String)
    group_id = Column(Integer, ForeignKey('groups.id'))
    group = relationship("Group", back_populates="users")


class Attendance(Base):
    __tablename__ = 'attendances'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="attendances")
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    lesson = relationship("Lesson", back_populates="attendances")
    grade = Column(Integer)
    participation = Column(Boolean, default=False)


class UserCourse(Base):
    __tablename__ = 'users_courses'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), primary_key=True)
    teacher = Column(Boolean, default=False)

    user = relationship("User", back_populates="courses")
    course = relationship("Course", back_populates="users")


# Define relationships
User.courses = relationship("Course", secondary="users_courses", back_populates="users")
Course.users = relationship("User", secondary="users_courses", back_populates="courses")
Lesson.attendances = relationship("Attendance", back_populates="lesson")
User.attendances = relationship("Attendance", back_populates="user")
Group.users = relationship("User", back_populates="group")

# Create an engine and tables
engine = create_engine('postgresql://bot:bot@localhost:5432/bot', echo=True)
Base.metadata.create_all(engine)
