
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt, JWTError
import bcrypt

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer


# ==========================================
# Load environment variables
# ==========================================

load_dotenv()


# ==========================================
# JWT Configuration
# ==========================================

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY is not set. "
        "Please add it to your .env file."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ==========================================
# Password Hashing
# ==========================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Bcrypt supports passwords up to 72 bytes.
    """

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError(
            "Password must be 72 bytes or fewer."
        )

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    """

    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        return False

    return bcrypt.checkpw(
        password_bytes,
        password_hash.encode("utf-8")
    )


# ==========================================
# Create JWT Access Token
# ==========================================

def create_access_token(user_id: int, role: str):

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "role": role,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ==========================================
# OAuth2
# ==========================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


# ==========================================
# Verify JWT Token
# ==========================================

def verify_token(
    token: str = Depends(oauth2_scheme)
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")
        role = payload.get("role")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid Token"
            )

        return {
            "user_id": int(user_id),
            "role": role
        }

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Token Expired or Invalid"
        )

