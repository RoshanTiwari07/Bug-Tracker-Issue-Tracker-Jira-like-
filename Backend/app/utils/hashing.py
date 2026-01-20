# Reusable utility functions
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_hash(plain: str, hashed: str) -> bool:
    """Verify a hash"""
    return pwd_context.verify(plain, hashed)
