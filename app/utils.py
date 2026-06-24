from datetime import datetime, timedelta, timezone
from uuid import uuid4
from pathlib import Path
import jwt
from fastapi import HTTPException
from starlette import status
from itsdangerous import Serializer, URLSafeSerializer, URLSafeTimedSerializer, BadSignature, SignatureExpired
from app.config import security_settings

_serializer = URLSafeTimedSerializer(security_settings.JWT_SECRET)

APP_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = APP_DIR/"templates"


def generate_access_token(
        data:dict,
        expiry = timedelta(days=1)
):
    token = jwt.encode(
        payload={
            **data,
            "jti":str(uuid4()),
            "exp": datetime.now(timezone.utc) + expiry,
        },
        algorithm=security_settings.JWT_ALGORITHM,
        key=security_settings.JWT_SECRET,
    )

    return token
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            security_settings.JWT_SECRET,
            algorithms=[security_settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

def generate_url_safe_token(data: dict, salt:str|None = None) -> str:
    return _serializer.dumps(data, salt = salt)


def decode_url_safe_token(token: str, salt:str|None = None, expiry: timedelta | None = None) -> dict | None:
    try:
        return _serializer.loads(
            token,
            salt=salt,
            max_age=expiry.total_seconds() if expiry else None,
        )
    except (BadSignature, SignatureExpired):
        return None