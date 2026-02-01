from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from schema.token import Token
from models.user import User
from schema.user import UserPublic, UserCreate, LoginRequest
from api.deps import get_db, get_current_user, rate_limit, ip_key
from service.user import create_user, authenticate_user
from core.jwt import create_access_token

from core.config import LOGIN_RATE_LIMIT, LOGIN_RATE_WINDOW_SECOND, SIGNUP_RATE_LIMIT, SIGNUP_RATE_WINDOW_SECOND

router = APIRouter(prefix="/auth", tags=["auth"])

login_rate_limiter = rate_limit(
    name="login",
    limit=LOGIN_RATE_LIMIT,
    window_second=LOGIN_RATE_WINDOW_SECOND,
    key_builder=ip_key
)

signup_rate_limiter = rate_limit(
    name="signup",
    limit=SIGNUP_RATE_LIMIT,
    window_second=SIGNUP_RATE_WINDOW_SECOND,
    key_builder=ip_key
)

@router.post(
    "/signup",
    response_model = UserPublic,
    status_code = status.HTTP_201_CREATED,
    dependencies = [Depends(signup_rate_limiter)]
)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        user = create_user(db, payload.username, payload.email, payload.password)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post(
    "/login",
    response_model = Token,
    status_code = status.HTTP_200_OK,
    dependencies = [Depends(login_rate_limiter)]
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    token = create_access_token(
        {
            "sub": str(user.id)
        }
    )

    return Token(access_token=token, user=user)

@router.get(
    "/me",
    response_model = UserPublic,
    status_code = status.HTTP_200_OK,
)
def me(current_user: User = Depends(get_current_user)):
    return current_user
