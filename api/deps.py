from jose import JWTError
from typing import Callable
from fastapi import status, HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from models.user import User
from core.jwt import decode_access_token
from service.user import get_user_by_id
from db.session import SessionLocal
from db.redis import redis_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)
KeyBuilder = Callable[[Request], str]

_LUA_INCR_EXPIRE="""
local current = redis.call("INCR", KEYS[1])
if current == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end
local ttl = redis.call("TTL", KEYS[1])
return {current, ttl}
"""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if not sub:
            raise credentials_exception
        user_id = int(sub)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = get_user_by_id(db, user_id)
    if not user:
        raise credentials_exception

    return user

def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> User | None:
    
    if not token:
        return None
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if not sub:
            raise credentials_exception
        user_id = int(sub)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    user = get_user_by_id(db, user_id)
    if not user:
        raise credentials_exception

    return user

def rate_limit(
        *,
        name: str,
        limit: int,
        window_second: int,
        key_builder: KeyBuilder
) -> Callable:
    
    async def _rate_limit(request: Request) -> None:
        key = f"{name}:{key_builder(request)}"

        try:
            count, ttl = redis_client.eval(_LUA_INCR_EXPIRE, 1, key, window_second)
        except Exception as e:
            return
        
        if int(count) > limit:
            headers = {}

            if isinstance(ttl, int) and ttl > 0:
                headers["Retry-After"] = str(ttl)
        
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {limit}/{window_second}s",
                headers=headers
            )
        
    return _rate_limit

def ip_key(request: Request) -> str:
    ip = request.client.host if request.client else "unknown"
    return f"ip:{ip}"

def user_key(user_id: int) -> Callable:
    def _user_key(_: Request) -> str:
        return f"user:{user_id}"
    return _user_key

