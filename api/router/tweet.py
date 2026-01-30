from fastapi import APIRouter, HTTPException, Response, status, Depends, Query, Path
from sqlalchemy.orm import Session

from service.tweet import create_tweet, list_tweets, get_tweet_by_id, update_tweet, delete_tweet, get_feed, get_tweet_by_id, get_list_replies
from schema.tweet import TweetPublic, TweetCreate, TweetUpdate
from api.deps import get_db, get_current_user, get_current_user_optional
from models.user import User


router = APIRouter(prefix="/tweet", tags=["tweet"])

@router.post(
    "",
    response_model=TweetPublic,
    status_code=status.HTTP_201_CREATED
)
def create_tweet_endpoint(
    payload: TweetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        tweet = create_tweet(db=db, body= payload.body, user_id=current_user.id, parent_id=payload.parent_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return tweet



@router.get(
    "/{tweet_id}/replies",
    response_model=list[TweetPublic],
    status_code=status.HTTP_200_OK
)
def get_list_replies_endpoint(
    tweet_id: int = Path(..., ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    replies = get_list_replies(db=db, tweet_id=tweet_id, user_id=user_id, skip=skip, limit=limit)
    if replies is None:
        raise HTTPException(status_code=404, detail="Tweet not found")
    return replies

@router.get(
    "",
    response_model=list[TweetPublic],
    status_code=status.HTTP_200_OK
)
def get_list_of_tweets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None

    tweet = list_tweets(db=db, skip=skip, limit=limit, user_id=user_id)
    return tweet



@router.patch(
    "/{tweet_id}",
    response_model=TweetPublic,
    status_code=status.HTTP_200_OK
)
def update_tweet_endpoint(
    tweet_id: int = Path(..., ge=1),
    payload: TweetUpdate = ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tweet = get_tweet_by_id(db=db, tweet_id=tweet_id, user_id=current_user.id)
    if not tweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )

    if tweet.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to edit this tweet"
        )

    updated_tweet = update_tweet(db=db, tweet=tweet, body=payload.body)
    return updated_tweet



@router.delete(
    "/{tweet_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_tweet_endpoint(
    tweet_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tweet = get_tweet_by_id(db=db, tweet_id=tweet_id, user_id=current_user.id)
    if not tweet:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tweet not found")

    if tweet.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete this tweet")

    delete_tweet(db=db, tweet=tweet)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get(
    "/feed",
    status_code=status.HTTP_200_OK,
    response_model=list[TweetPublic]
)
def get_feed_endpoint(
    skip: int = Query(0, ge=0),
    limit: int  = Query(20, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    list_of_tweets = get_feed(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return list_of_tweets

@router.get(
        "/{tweet_id}",
        response_model=TweetPublic,
        status_code=status.HTTP_200_OK
)
def get_tweet_by_id_endpoint(
    tweet_id: int,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None

    tweet = get_tweet_by_id(db=db, tweet_id=tweet_id, user_id=user_id)
    if tweet is None:
        raise HTTPException(status_code=404, detail="Tweet not found")

    return tweet
