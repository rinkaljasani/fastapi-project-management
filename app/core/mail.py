from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from jose import JWTError, jwt, ExpiredSignatureError


from app.core.config import settings
def create_verification_token(email: str) -> str:
        payload = {
            "sub": email,
            "type": "email_verification",
            "exp": datetime.now(timezone.utc) + timedelta(hours=24)
        }

        return jwt.encode(
            payload,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )


def decode_verification_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        if payload.get("type") != "email_verification":
            raise HTTPException(
                status_code=400,
                detail="Invalid verification token"
            )

        email = payload.get("sub")

        if not email:
            raise HTTPException(
                status_code=400,
                detail="Email not found in token"
            )

        return email

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=400,
            detail="Verification link expired"
        )

    except InvalidTokenError:
        raise HTTPException(
            status_code=400,
            detail="Invalid verification token"
        )