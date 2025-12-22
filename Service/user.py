from sqlalchemy.orm import Session
from sqlalchemy import select
from models.user import User
from core.security import hash_password, verify_password


def get_user_by_username(db: Session, username:str) -> User | None:
    stmt = select(User).where(User.username == username)
    return db.scalar(stmt)

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
        hash_password = hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    
    if not user:
        return None
    
    if not user.is_active:
        return None
    
    if not verify_password(password, user.password_hash):
        return None



    return None

