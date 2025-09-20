"""
JWT Utilities - issue and verify access/refresh tokens
"""

import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional


JWT_SECRET = os.environ.get('JWT_SECRET_KEY') or os.environ.get('SECRET_KEY', 'change-me')
JWT_ALG = os.environ.get('JWT_ALGORITHM', 'HS256')
ACCESS_EXPIRES_MIN = int(os.environ.get('JWT_ACCESS_MINUTES', '30'))
REFRESH_EXPIRES_DAYS = int(os.environ.get('JWT_REFRESH_DAYS', '7'))


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(identity: str, role: str, extra: Optional[Dict[str, Any]] = None) -> str:
    payload: Dict[str, Any] = {
        'sub': identity,
        'role': role,
        'type': 'access',
        'iat': int(_now().timestamp()),
        'exp': int((_now() + timedelta(minutes=ACCESS_EXPIRES_MIN)).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def create_refresh_token(identity: str) -> str:
    payload: Dict[str, Any] = {
        'sub': identity,
        'type': 'refresh',
        'iat': int(_now().timestamp()),
        'exp': int((_now() + timedelta(days=REFRESH_EXPIRES_DAYS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])


