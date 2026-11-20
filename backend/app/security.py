from datetime import datetime, timedelta, timezone
from typing import Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET
from .excel_handler import find_row


password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def create_access_token(account: Dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(account["UID"]),
        "uid": str(account["UID"]),
        "role": str(account["Role"]),
        "mid": "" if account.get("MID") in (None, "") else str(account["MID"]),
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        uid = payload.get("uid")
        if not uid:
            raise JWTError("missing uid")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    account = find_row("Accounts", "UID", uid)
    if not account or account.get("Status") != "Active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")
    return account


def require_librarian(account: Dict = Depends(get_current_account)) -> Dict:
    if account.get("Role") != "Librarian":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Librarian access required")
    return account


def require_member(account: Dict = Depends(get_current_account)) -> Dict:
    if account.get("Role") != "Member":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Member access required")
    return account
