import datetime
from uuid import uuid4

from sqlalchemy import DateTime, func, String, UUID
from sqlalchemy.orm import declared_attr, Mapped, mapped_column


class CreatedUpdatedMixin:
    @declared_attr
    def created_at(self) -> Mapped[datetime]:
        return mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    @declared_attr
    def updated_at(self) -> Mapped[datetime]:
        return mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class TimestampMixin(CreatedUpdatedMixin):
    @declared_attr
    def modifiedon(self) -> Mapped[datetime]:
        return mapped_column(DateTime(timezone=True), nullable=True)


class IdUuidMixin:
    @declared_attr
    def id(self) -> Mapped[str]:
        return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4, insert_default=uuid4)
