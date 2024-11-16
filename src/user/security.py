from passlib.context import CryptContext

password_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_ctx.hash(password)


def check_password(password: str, db_password_hash: str) -> bool:
    return password_ctx.verify(db_password_hash, hash=db_password_hash)
