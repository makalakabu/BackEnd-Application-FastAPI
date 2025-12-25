from fastapi import FastAPI
from api.router import user, auth

app = FastAPI()

app.include_router(auth.router)


