from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, desc
from models.tweet import Tweet


def create_tweet(db: Session, body: str, user_id: int) -> Tweet:
    tweet = Tweet(body=body, user_id=user_id)

    db.add(tweet)
    db.commit()
    db.refresh(tweet)

    return tweet

def get_tweet_by_id(db:Session, tweet_id:int) -> Tweet | None:
    stmt = select(Tweet).options(selectinload(Tweet.user)).where(Tweet.id == tweet_id)
    
    return db.scalar(stmt)

def list_tweets(db: Session, skip: int = 0, limit: int = 20) -> list[Tweet]:
    stmt = (
        select(Tweet)
        .options(selectinload(Tweet.user))
        .order_by(desc(Tweet.created_at))
        .offset(skip)
        .limit(limit)
    )

    return db.scalars(stmt).all()

def update_tweet(db:Session, tweet: Tweet, body: str) -> Tweet:
    tweet.body = body
    db.add(tweet)
    db.commit()
    db.refresh(tweet)

    return tweet

def delete_tweet(db: Session, tweet: Tweet) -> None:
    db.delete(tweet)
    db.commit()