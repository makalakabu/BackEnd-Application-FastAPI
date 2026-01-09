from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, status, Depends, Query

from models.user import User
from schema.user import UserPublic, UserProfile, UserUpdate
from service.user import get_user_by_username
from api.deps import get_db, get_current_user
from service.user import get_user_profile_by_username, update_user_profile
from service.follow import follow_user, unfollow_user, list_of_followers, list_of_following

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
def follow_username(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = get_user_by_username(db=db, username=username)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        follow_user(db=db, follower_id=current_user.id, following_id=target.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    

@router.delete("/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow_username(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = get_user_by_username(db=db, username=username)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        unfollow_user(db=db, follower_id=current_user.id, following_id=target.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get(
    "/{username}/followers",
    response_model=list[UserPublic],
    status_code=status.HTTP_200_OK,
)
def get_followers(
    username: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=20),
    db: Session = Depends(get_db),
):
    target = get_user_by_username(db=db, username=username)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    followers = list_of_followers(db=db, user_id=target.id, skip=skip, limit=limit)
    return followers


@router.get(
    "/{username}/following",
    response_model=list[UserPublic],
    status_code=status.HTTP_200_OK,
)
def get_following(
    username: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=20),
    db: Session = Depends(get_db),
):
    target = get_user_by_username(db=db, username=username)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    following = list_of_following(db=db, user_id=target.id, skip=skip, limit=limit)
    return following

@router.get(
    "/{username}",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK
)
def get_user_profile(
    username: str,
    db: Session = Depends(get_db)
):
    result = get_user_profile_by_username(db, username)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    user, followers_count, following_count = result
    return {
        "username": user.username,
        "email": user.email,
        "bio": user.bio,
        "image": user.image,
        "followers_count": followers_count,
        "following_count": following_count,
    }


@router.patch(
    "/me",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK
)
def patch_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = update_user_profile(db=db, user=current_user, data=payload)
    return user