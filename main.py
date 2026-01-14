from fastapi import FastAPI
from api.router import user, auth, tweet

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.include_router(auth.router)
app.include_router(tweet.router)
app.include_router(user.router)


