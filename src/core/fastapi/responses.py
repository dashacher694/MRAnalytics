"""
Error response like in calendar_service
"""
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    title: str
    description: str
    extra: any = None
