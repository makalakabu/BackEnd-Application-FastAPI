from pydantic import BaseModel

from schema.user import UserPublic

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic