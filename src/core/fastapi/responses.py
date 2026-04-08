"""
Error response like in calendar_service
"""
from typing import Any
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    title: str
    description: str
    extra: Any = None
