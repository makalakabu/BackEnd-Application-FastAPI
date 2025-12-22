from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hashing_pwd(password: str) -> str:
    return pwd_context.hash(password)

def verify_pwd(password: str) -> bool:
    return pwd_context.verify(password)

