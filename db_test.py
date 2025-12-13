from db.session import SessionLocal, engine
from models.user import User
from db.db_base import Base

def dbRun():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = User(username="test1",
                    email="test@ytest.com",
                    password_hash="12345678"
                    )
        db.add(user)
        db.commit()
        db.refresh(user)

        user1 = db.query(User).filter(User.id == user.id).first()
        print("name: "+user1.username)
        print("email: "+user1.email)
        print("password: "+user1.password_hash)

    finally:
        db.close

if __name__ == "__main__":
    dbRun()