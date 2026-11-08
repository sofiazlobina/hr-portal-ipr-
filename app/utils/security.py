from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        if hashed_password.startswith('pbkdf2_sha256$'):
            _, iterations, salt, expected = hashed_password.split('$')
            count = int(iterations)
            if not 1 <= count <= 2_000_000:
                return False
            actual = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'),
                                       base64.b64decode(salt, validate=True), count)
            return hmac.compare_digest(actual, base64.b64decode(expected, validate=True))
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except (ValueError, TypeError):
        return False


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    payload = data.copy()
    if 'sub' in payload:
        payload['sub'] = str(payload['sub'])
    payload['exp'] = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=401, detail='Не удалось проверить учётные данные',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM],
                             options={'require_exp': True, 'require_sub': True})
        subject = payload['sub']
        if not isinstance(subject, str) or not subject.isascii() or not subject.isdecimal():
            raise credentials_exception
        user_id = int(subject)
        if not 0 < user_id <= 2147483647:
            raise credentials_exception
    except (JWTError, ValueError, KeyError):
        raise credentials_exception
    user = db.get(User, user_id)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=403, detail='Пользователь деактивирован')
    return user
