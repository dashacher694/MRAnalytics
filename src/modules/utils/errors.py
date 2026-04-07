"""
Simple domain exceptions like in calendar_service
"""


class NotFoundError(Exception):
    pass


class BadRequestError(Exception):
    pass


class ConflictError(Exception):
    pass
