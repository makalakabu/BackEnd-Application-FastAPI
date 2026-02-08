from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from models.follow import Follow
from models.follow_request import FollowRequest
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

def create_follow_request(db: Session, user_id: int, target_id:int) -> None:
    if user_id == target_id:
        raise ValueError("Cannot Follow Yourself")
    
    exist = db.scalar(
        select(Follow).where(
            Follow.follower_id==user_id,
            Follow.following_id==target_id
        )
    )
    if exist:
        raise ValueError("Already Following")
    
    existing_request = db.scalar(
        select(FollowRequest).where(
            FollowRequest.requester_id == user_id,
            FollowRequest.target_id == target_id,
        )
    )
    if existing_request:
        raise ValueError("Follow request already pending")
    
    follow_request = FollowRequest(requester_id=user_id, target_id=target_id)
    
    db.add(follow_request)

def accept_follow_request(db: Session, user_id: int, target_id: int) -> None:
    follow_request = db.scalar(
        select(FollowRequest).where(
        FollowRequest.requester_id == user_id,
        FollowRequest.target_id == target_id,
        )
    )
    if follow_request is None:
        raise ValueError("Follow Request Not Found")
    
    follow = Follow(follower_id=user_id, following_id=target_id)
    db.add(follow)
    db.delete(follow_request)

def delete_follow_request(db: Session, user_id: int, target_id: int) -> None:
    follow_request = db.scalar(
        select(FollowRequest).where(
        FollowRequest.requester_id == user_id,
        FollowRequest.target_id == target_id,
        )
    )
    if follow_request is None:
        raise ValueError("Follow Request Not Found")
    
    db.delete(follow_request)
        

def list_of_follow_request(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> list[User]:
    stmt = (
        select(User)
        .join(FollowRequest, User.id==FollowRequest.requester_id)
        .where(FollowRequest.target_id==user_id)
        .order_by(desc(FollowRequest.created_at))
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(stmt).all())
