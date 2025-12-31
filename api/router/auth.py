from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from schema.token import Token
from models.user import User
from schema.user import UserPublic, UserCreate, LoginRequest
from api.deps import get_db, get_current_user
from service.user import create_user, authenticate_user
from core.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/signup",
    response_model = UserPublic,
    status_code = 201,
    description = "Create New User"
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
    status_code = 200,
    description = "Loging in existed user"
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
    status_code = 200,
    description = "Protected Endpoint"
)
def me(current_user: User = Depends(get_current_user)):
    return current_user