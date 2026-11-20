from typing import Dict

from fastapi import APIRouter, Depends, HTTPException

from ..excel_handler import append_row, find_row, find_rows, next_id, read_rows, update_row
from ..models import MemberCreate, MemberStatusUpdate, MemberUpdate
from ..security import hash_password, require_librarian, require_member


router = APIRouter(prefix="/members", tags=["Members"])


@router.get("")
def list_members(account: Dict = Depends(require_librarian)) -> list:
    return read_rows("Members")


@router.get("/{mid}")
def get_member(mid: str, account: Dict = Depends(require_librarian)) -> Dict:
    member = find_row("Members", "MID", mid)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.post("", status_code=201)
def create_member(request: MemberCreate, account: Dict = Depends(require_librarian)) -> Dict:
    if find_row("Members", "Email", str(request.email)):
        raise HTTPException(status_code=409, detail="Email already exists")
    if find_row("Accounts", "Username", request.username):
        raise HTTPException(status_code=409, detail="Username already exists")

    mid = next_id("Members", "MID", "M")
    uid = next_id("Accounts", "UID", "U")
    from datetime import date
    today = date.today()
    expiry = date.fromordinal(today.toordinal() + 365)
    append_row("Members", {
        "MID": mid, "FName": request.fname, "LName": request.lname,
        "Phone": request.phone, "Email": str(request.email),
        "Address": request.address, "JoinDate": today, "ExpiryDate": expiry,
        "Status": "Active",
    })
    append_row("Accounts", {
        "UID": uid, "Username": request.username,
        "PasswordHash": hash_password(request.password),
        "Role": "Member", "MID": mid, "Status": "Active",
    })
    return {"MID": mid, "UID": uid, "Status": "Active"}


@router.put("/{mid}")
def update_member(mid: str, request: MemberUpdate, account: Dict = Depends(require_librarian)) -> Dict:
    member = find_row("Members", "MID", mid)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    changes = {}
    field_map = {
        "fname": "FName", "lname": "LName", "phone": "Phone",
        "email": "Email", "address": "Address",
    }
    for field, column in field_map.items():
        value = getattr(request, field)
        if value is not None:
            changes[column] = str(value) if column == "Email" else value
    updated = update_row("Members", "MID", mid, changes)
    return updated or {}


@router.patch("/{mid}/status")
def change_member_status(
    mid: str,
    request: MemberStatusUpdate,
    account: Dict = Depends(require_librarian),
) -> Dict:
    member = find_row("Members", "MID", mid)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if request.status == "Inactive":
        for loan in find_rows("BorrowList", "MID", mid):
            if loan.get("Status") == "Approved":
                raise HTTPException(status_code=409, detail="Member has active loans")
    update_row("Members", "MID", mid, {"Status": request.status})
    for member_account in find_rows("Accounts", "MID", mid):
        update_row("Accounts", "UID", member_account["UID"], {"Status": "Active" if request.status == "Active" else "Inactive"})
    return {"MID": mid, "Status": request.status}


@router.post("/{mid}/cancel")
def cancel_membership(mid: str, account: Dict = Depends(require_member)) -> Dict:
    if str(account.get("MID", "")) != mid:
        raise HTTPException(status_code=403, detail="You may cancel only your own membership")
    member = find_row("Members", "MID", mid)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    for loan in find_rows("BorrowList", "MID", mid):
        if loan.get("Status") == "Approved":
            raise HTTPException(status_code=409, detail="Return all active loans before cancelling")
    update_row("Members", "MID", mid, {"Status": "Inactive"})
    update_row("Accounts", "UID", account["UID"], {"Status": "Inactive"})
    return {"MID": mid, "Status": "Inactive"}
