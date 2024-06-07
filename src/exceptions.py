class LogicError(Exception):
    """End-user logical error"""


class NotFoundError(Exception):
    """Data not found via Data Access"""


class CourseNotFoundError(NotFoundError):
    """Course not found"""


class StudentNotFoundError(NotFoundError):
    """Student not found"""


class LessonNotFoundError(NotFoundError):
    """Student not found"""
