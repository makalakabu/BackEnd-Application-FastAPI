from datetime import datetime
from sqlalchemy import UniqueConstraint, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db_base import Base

class FollowRequest(Base):
    __tablename__ = "follow_requests"
    __table_args__ = (
        UniqueConstraint("requester_id", "target_id", name="uq_follow_request_pair"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    requester = relationship("User", foreign_keys=[requester_id])
    targeter = relationship("User", foreign_keys=[target_id])

    

