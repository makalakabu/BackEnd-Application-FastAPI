from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from schema.user import UserInTweet


class TweetCreate(BaseModel):
    body: str = Field(min_length=1, max_length=280)


class TweetUpdate(BaseModel):
    body: str | None = Field(default=None, min_length=1, max_length=280)


class TweetPublic(BaseModel):
    id: int
    body: str
    created_at: datetime
    user: UserInTweet

    model_config = ConfigDict(from_attributes=True)
