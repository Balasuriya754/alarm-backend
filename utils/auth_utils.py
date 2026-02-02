from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from redis_client import redis_client

security = HTTPBearer()
SESSION_TTL = 5 * 24 * 60 * 60

def verify_session(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials  # ← extracted Bearer token

    try:
        phone_num = redis_client.get(f"session:{token}")
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Authentication service temporarily unavailable"
        )

    if not phone_num:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid"
        )

    phone_num = phone_num.decode() if isinstance(phone_num, bytes) else phone_num

    # single-device enforcement
    active_token = redis_client.get(f"user_session:{phone_num}")
    if not active_token:
        raise HTTPException(status_code=401, detail="Session expired")

    active_token = (
        active_token.decode()
        if isinstance(active_token, bytes)
        else active_token
    )

    if active_token != token:
        raise HTTPException(
            status_code=401,
            detail="Session revoked (logged in from another device)"
        )

    # sliding expiry
    try:
        redis_client.expire(f"session:{token}", SESSION_TTL)
        redis_client.expire(f"user_session:{phone_num}", SESSION_TTL)
    except Exception:
        pass

    return phone_num
