from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.modules.seedwork.mixin import IdUuidMixin, TimestampMixin
from src.persistance.base import Base


class MRMetricsEntity(Base, IdUuidMixin, TimestampMixin):
    
    __tablename__ = "metrics"
    
    mr_iid: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    merged_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    web_url: Mapped[str] = mapped_column(String, nullable=False)
    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)
    time_to_merge: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_rounds: Mapped[int] = mapped_column(Integer, default=0)
    comment_density: Mapped[float] = mapped_column(Float, default=0.0)
    formal_approval: Mapped[int] = mapped_column(Integer, default=0)
    response_time_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    num_comments: Mapped[int] = mapped_column(Integer, default=0)
    num_approvals: Mapped[int] = mapped_column(Integer, default=0)
    changes_requested: Mapped[int] = mapped_column(Integer, default=0)
    
    def __repr__(self) -> str:
        return f"<MRMetrics(mr_iid={self.mr_iid}, author={self.author}, title='{self.title[:30]}...', risk_score={getattr(self, 'risk_score', 'N/A')})>"
