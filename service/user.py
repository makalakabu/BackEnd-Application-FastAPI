from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.follow import Follow
from models.user import User
from schema.user import UserUpdate
from core.security import hash_password, verify_password

def get_user_by_id(db: Session, id:int) -> User | None:
    stmt = select(User).where(User.id == id)
    return db.scalar(stmt)

def get_user_by_username(db: Session, username:str) -> User | None:
    stmt = select(User).where(User.username == username)
    return db.scalar(stmt)

def get_user_profile_by_username(db: Session, username:str) -> tuple[User, int, int] | None:
    user = get_user_by_username(db=db, username=username)
    if not user:
        return None

    follower_count = db.scalar(
        select(func.count()).select_from(Follow).where(Follow.following_id==user.id)
    ) or 0

    following_count = db.scalar(
        select(func.count()).select_from(Follow).where(Follow.follower_id==user.id)
    ) or 0

    return user, follower_count, following_count

def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)

def create_user(db: Session, username: str, email: str, password: str) -> User:
    if get_user_by_email(db, email):
        raise ValueError("Email Already Exist")
    
    if get_user_by_username(db, username):
        raise ValueError("Username Already Exist")
    
    user = User(
        username = username,
        email = email,
        password_hash = hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None

    return user

def update_user_profile(db: Session, user: User, data: UserUpdate) -> User:
    payload = data.model_dump(exclude_unset=True)

    for key, value in payload.items():
        setattr(user, key, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
