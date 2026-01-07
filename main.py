from fastapi import FastAPI
from api.router import user, auth, tweet

app = FastAPI()

app.include_router(auth.router)
app.include_router(tweet.router)
app.include_router(user.router)


