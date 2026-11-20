from datetime import date
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status

from ..config import MEMBERSHIP_FEE
from ..excel_handler import append_row, find_row, find_rows, next_id, read_rows, update_row
from ..models import LoginRequest, LoginResponse, RegistrationRequest
from ..security import create_access_token, get_current_account, hash_password, require_librarian, verify_password


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest) -> Dict:
    account = find_row("Accounts", "Username", request.username)
    if not account or account.get("Status") != "Active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if not verify_password(request.password, str(account["PasswordHash"])):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = create_access_token(account)
    return {
        "access_token": token,
        "role": account["Role"],
        "uid": account["UID"],
        "mid": account.get("MID") or None,
        "username": account["Username"],
    }


@router.post("/register", status_code=201)
def register(request: RegistrationRequest) -> Dict:
    for account in find_rows("Accounts", "Username", request.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    for registration in read_pending_by_email(str(request.email)):
        raise HTTPException(status_code=409, detail="A pending registration already exists for this email")
    if find_row("Members", "Email", str(request.email)):
        raise HTTPException(status_code=409, detail="Email already belongs to a member")

    rid = next_id("RegistrationRequests", "RID", "R")
    append_row("RegistrationRequests", {
        "RID": rid,
        "FName": request.fname,
        "LName": request.lname,
        "Phone": request.phone,
        "Email": str(request.email),
        "Address": request.address,
        "RequestDate": date.today(),
        "MembershipPayment": 0,
        "Status": "Pending",
        "Username": request.username,
        "PasswordHash": hash_password(request.password),
    })
    return {"RID": rid, "Status": "Pending", "message": "Registration request submitted"}


def read_pending_by_email(email: str) -> list:
    return [
        row for row in read_rows("RegistrationRequests")
        if str(row.get("Email", "")).lower() == email.lower()
        and row.get("Status") == "Pending"
    ]


@router.get("/me")
def me(account: Dict = Depends(get_current_account)) -> Dict:
    return account


@router.get("/registrations")
def list_registrations(account: Dict = Depends(require_librarian)) -> list:
    from ..excel_handler import read_rows
    return read_rows("RegistrationRequests")


@router.patch("/registrations/{rid}/approve")
def approve_registration(rid: str, account: Dict = Depends(require_librarian)) -> Dict:
    registration = find_row("RegistrationRequests", "RID", rid)
    if not registration:
        raise HTTPException(status_code=404, detail="Registration request not found")
    if registration.get("Status") != "Pending":
        raise HTTPException(status_code=409, detail="Registration request is no longer pending")

    if find_row("Members", "Email", registration["Email"]):
        raise HTTPException(status_code=409, detail="Email already belongs to a member")

    mid = next_id("Members", "MID", "M")
    today = date.today()
    expiry = date.fromordinal(today.toordinal() + 365)
    append_row("Members", {
        "MID": mid,
        "FName": registration["FName"],
        "LName": registration["LName"],
        "Phone": registration["Phone"],
        "Email": registration["Email"],
        "Address": registration["Address"],
        "JoinDate": today,
        "ExpiryDate": expiry,
        "Status": "Active",
    })

    uid = next_id("Accounts", "UID", "U")
    append_row("Accounts", {
        "UID": uid,
        "Username": registration["Username"],
        "PasswordHash": registration["PasswordHash"],
        "Role": "Member",
        "MID": mid,
        "Status": "Active",
    })
    update_row("RegistrationRequests", "RID", rid, {
        "MembershipPayment": MEMBERSHIP_FEE,
        "Status": "Approved",
    })
    return {"RID": rid, "MID": mid, "UID": uid, "Status": "Approved"}


@router.patch("/registrations/{rid}/reject")
def reject_registration(rid: str, account: Dict = Depends(require_librarian)) -> Dict:
    registration = find_row("RegistrationRequests", "RID", rid)
    if not registration:
        raise HTTPException(status_code=404, detail="Registration request not found")
    if registration.get("Status") != "Pending":
        raise HTTPException(status_code=409, detail="Registration request is no longer pending")
    update_row("RegistrationRequests", "RID", rid, {"Status": "Rejected"})
    return {"RID": rid, "Status": "Rejected"}
