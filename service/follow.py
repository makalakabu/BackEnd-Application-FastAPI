from sqlalchemy.orm import Session
from sqlalchemy import select

from models.follow import Follow
from models.user import User

def follow_user(db: Session, follower_id: int, following_id: int) -> None:

    if follower_id == following_id:
        raise ValueError("Cannot Follow Yourself")
    
    exist = db.scalar(
        select(Follow).where(
            Follow.follower_id==follower_id,
            Follow.following_id==following_id
        )
    )
    if exist:
        raise ValueError("Already Following")

    follow = Follow(
        follower_id=follower_id,
        following_id=following_id
    )
    db.add(follow)
    db.commit()
    db.refresh(follow)


def unfollow_user(db: Session, follower_id: int, following_id: int) -> None:

    if follower_id == following_id:
        raise ValueError("Cannot Unfollow Yourself")
    
    unfollow = db.scalar(
        select(Follow).where(
            Follow.follower_id==follower_id,
            Follow.following_id==following_id
        )
    )
    if unfollow is None:
        raise ValueError("Not Following this User")


    db.delete(unfollow)
    db.commit()

def list_of_following(db: Session, user_id: int,  skip: int = 0, limit: int = 20) -> list[User]:
    stmt = (
        select(User)
        .join(Follow, Follow.following_id == User.id)
        .where(Follow.follower_id == user_id)
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(stmt).all())

def list_of_followers(db: Session, user_id: int,  skip: int = 0, limit: int = 20) -> list[User]:
    stmt = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(Follow.following_id == user_id)
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(stmt).all())
