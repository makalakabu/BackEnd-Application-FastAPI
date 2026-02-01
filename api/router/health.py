from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from api.deps import get_db
from db.redis import redis_client

router = APIRouter(tags=["health"], prefix="/health")

@router.get("", status_code=200)
def health(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database Unavailable")
    
    return {"status" :"ok", "db": "ok"}

@router.get("/redis", status_code=status.HTTP_200_OK)
def health_redis():
    try:
        redis_client.ping()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Redis Unavailable {e}")
    
    return{"status" : "ok"}