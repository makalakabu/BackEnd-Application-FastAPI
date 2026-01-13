from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, desc, or_, literal, exists, and_
from models.user import User
from models.tweet import Tweet
from models.follow import Follow


def create_tweet(db: Session, body: str, user_id: int) -> Tweet:
    tweet = Tweet(body=body, user_id=user_id)

    db.add(tweet)
    db.commit()
    db.refresh(tweet)

    return tweet

def get_tweet_by_id(db:Session, tweet_id:int, user_id: int | None) -> Tweet | None:
    stmt = select(Tweet).options(selectinload(Tweet.user)).where(Tweet.id == tweet_id)
    tweet = db.scalar(stmt)

    if tweet is None:
        return None
    
    author = tweet.user

    if not author.is_private:
        return tweet
    
    if user_id is None:
        return None
    
    if user_id == author.id:
        return tweet
    
    exist = db.scalar(
        select(Follow)
        .where(
            Follow.following_id==author.id,
            Follow.follower_id==user_id
        )
    )
    if not exist:
        return None
    
    return tweet

def list_tweets(db: Session, skip: int = 0, limit: int = 20, user_id: int | None = None) -> list[Tweet]:
    viewer_id = literal(user_id)  

    allowed_author = or_(
        User.is_private == False,         
        User.id == viewer_id,              
        exists(
            select(1).where(
                and_(
                    Follow.follower_id == viewer_id,
                    Follow.following_id == User.id,
                )
            )
        ),                                
    )

    stmt = (
        select(Tweet)
        .join(User, User.id == Tweet.user_id)
        .options(selectinload(Tweet.user))
        .where(allowed_author)
        .order_by(desc(Tweet.created_at))
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(stmt).all())
    
        
def update_tweet(db:Session, tweet: Tweet, body: str) -> Tweet:
    tweet.body = body
    db.add(tweet)
    db.commit()
    db.refresh(tweet)

    return tweet

def delete_tweet(db: Session, tweet: Tweet) -> None:
    db.delete(tweet)
    db.commit()

def get_feed(db: Session, user_id: int,  skip: int = 0, limit: int = 20) -> list[Tweet]:
    following_user_id = (
        select(Follow.following_id)
        .where(Follow.follower_id==user_id)
    )

    stmt = (
        select(Tweet)
        .options(selectinload(Tweet.user))
        .where(
            or_(
                Tweet.user_id==user_id,
                Tweet.user_id.in_(following_user_id)
            )
        )
        .order_by(desc(Tweet.created_at))
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(stmt).all())