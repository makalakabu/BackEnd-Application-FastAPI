from __future__ import annotations

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db_base import Base


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    body: Mapped[str] = mapped_column(String(280), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("tweets.id", ondelete="CASCADE"), nullable=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship("User", back_populates="tweets")
    parent:Mapped["Tweet | None"] = relationship("Tweet", back_populates="replies", remote_side="Tweet.id")
    replies: Mapped[list["Tweet"]] = relationship("Tweet", back_populates="parent", cascade="all, delete-orphan")


    
