from fastapi import APIRouter

router = APIRouter()

@router.get("/user/test")
async def get_hello():
    return {"message" : "Hello World!"}