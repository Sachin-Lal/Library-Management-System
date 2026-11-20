from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..config import FINE_PER_DAY
from ..excel_handler import append_row, find_row, find_rows, next_id, parse_date, read_rows, update_row
from ..security import get_current_account, require_librarian


class CalculateFineRequest(BaseModel):
    tid: str = Field(min_length=1)


class PaymentRequest(BaseModel):
    amount: float = Field(gt=0)


router = APIRouter(prefix="/fines", tags=["Fines"])


@router.get("")
def list_fines(account: Dict = Depends(require_librarian)) -> list:
    return read_rows("LateList")


@router.get("/member/{mid}")
def member_fines(mid: str, account: Dict = Depends(get_current_account)) -> list:
    if account.get("Role") != "Librarian" and str(account.get("MID", "")) != mid:
        raise HTTPException(status_code=403, detail="You may view only your own fines")
    result = []
    for transaction in find_rows("BorrowList", "MID", mid):
        result.extend(find_rows("LateList", "TID", transaction["TID"]))
    return result


@router.post("/calculate")
def calculate_fine(request: CalculateFineRequest, account: Dict = Depends(require_librarian)) -> Dict:
    transaction = find_row("BorrowList", "TID", request.tid)
    if not transaction:
        raise HTTPException(status_code=404, detail="Borrowing transaction not found")
    due_date = parse_date(transaction.get("DueDate"))
    if not due_date:
        raise HTTPException(status_code=409, detail="Transaction has not been approved")

    return_date = parse_date(transaction.get("RDate"))
    if return_date:
        reference_date = return_date
    elif transaction.get("Status") == "Approved":
        from datetime import date
        reference_date = date.today()
    else:
        reference_date = None
    if reference_date is None:
        raise HTTPException(status_code=409, detail="Fine cannot be calculated for this transaction")

    days_late = max(0, (reference_date - due_date).days)
    fine_due = days_late * FINE_PER_DAY
    existing = find_rows("LateList", "TID", request.tid)
    if existing:
        fine = existing[0]
        if fine["PaymentStatus"] == "Paid":
            return fine
        paid = float(fine["AmountPaid"])
        update_row("LateList", "LID", fine["LID"], {
            "DaysLate": days_late,
            "FineDue": fine_due,
            "PaymentStatus": "Paid" if paid >= fine_due else ("Partial" if paid > 0 else "Unpaid"),
        })
        return find_row("LateList", "LID", fine["LID"]) or {}

    if days_late == 0:
        return {"TID": request.tid, "DaysLate": 0, "FineDue": 0, "AmountPaid": 0, "PaymentStatus": "Paid"}
    lid = next_id("LateList", "LID", "L")
    append_row("LateList", {
        "LID": lid,
        "TID": request.tid,
        "DaysLate": days_late,
        "FineDue": fine_due,
        "AmountPaid": 0,
        "PaymentStatus": "Unpaid",
    })
    return find_row("LateList", "LID", lid) or {}


@router.patch("/{lid}/pay")
def pay_fine(lid: str, request: PaymentRequest, account: Dict = Depends(require_librarian)) -> Dict:
    fine = find_row("LateList", "LID", lid)
    if not fine:
        raise HTTPException(status_code=404, detail="Fine not found")
    amount_paid = float(fine["AmountPaid"])
    fine_due = float(fine["FineDue"])
    remaining = fine_due - amount_paid
    if remaining <= 0:
        raise HTTPException(status_code=409, detail="Fine is already paid")
    if request.amount > remaining:
        raise HTTPException(status_code=422, detail="Payment exceeds the remaining fine")

    new_paid = amount_paid + request.amount
    payment_status = "Paid" if new_paid >= fine_due else "Partial"
    update_row("LateList", "LID", lid, {
        "AmountPaid": new_paid,
        "PaymentStatus": payment_status,
    })
    return find_row("LateList", "LID", lid) or {}
