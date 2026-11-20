from datetime import date, timedelta
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException

from ..config import LOAN_PERIOD_DAYS, MAX_ACTIVE_LOANS
from ..excel_handler import append_row, find_row, find_rows, next_id, parse_date, read_rows, update_row
from ..models import BorrowRequestCreate, ReturnRequest
from ..security import get_current_account, require_librarian, require_member


router = APIRouter(prefix="/borrow", tags=["Borrowing"])


@router.post("/request", status_code=201)
def create_borrow_request(
    request: BorrowRequestCreate,
    account: Dict = Depends(require_member),
) -> Dict:
    mid = str(account.get("MID", ""))
    member = find_row("Members", "MID", mid)
    if not member or member.get("Status") != "Active":
        raise HTTPException(status_code=409, detail="Only approved active members may borrow")
    if member.get("ExpiryDate") and parse_date(member["ExpiryDate"]) < date.today():
        raise HTTPException(status_code=409, detail="Membership has expired")

    for transaction in find_rows("BorrowList", "MID", mid):
        for fine in find_rows("LateList", "TID", transaction["TID"]):
            if fine.get("PaymentStatus") != "Paid":
                raise HTTPException(status_code=409, detail="Outstanding fines must be paid before borrowing")

    active_count = sum(
        1 for loan in find_rows("BorrowList", "MID", mid)
        if loan.get("Status") == "Approved"
    )
    if active_count >= MAX_ACTIVE_LOANS:
        raise HTTPException(status_code=409, detail="Maximum active loan limit reached")

    book = find_row("Books", "BID", request.bid)
    if not book or book.get("Status") != "Active":
        raise HTTPException(status_code=404, detail="Book not found or inactive")
    if int(book["AvailableCopies"]) <= 0:
        raise HTTPException(status_code=409, detail="No copy is currently available")

    existing = [
        loan for loan in find_rows("BorrowList", "MID", mid)
        if loan.get("BID") == request.bid and loan.get("Status") in {"Pending", "Approved"}
    ]
    if existing:
        raise HTTPException(status_code=409, detail="A pending or active request already exists for this book")

    tid = next_id("BorrowList", "TID", "T")
    append_row("BorrowList", {
        "TID": tid,
        "MID": mid,
        "BID": request.bid,
        "BDate": "",
        "DueDate": "",
        "RDate": "",
        "Status": "Pending",
        "RequestDate": date.today(),
    })
    return {"TID": tid, "MID": mid, "BID": request.bid, "Status": "Pending"}


@router.get("/requests")
def list_requests(account: Dict = Depends(require_librarian)) -> list:
    return [
        row for row in read_rows("BorrowList")
        if row.get("Status") == "Pending"
    ]


@router.patch("/{tid}/approve")
def approve_borrowing(tid: str, account: Dict = Depends(require_librarian)) -> Dict:
    transaction = find_row("BorrowList", "TID", tid)
    if not transaction:
        raise HTTPException(status_code=404, detail="Borrowing transaction not found")
    if transaction.get("Status") != "Pending":
        raise HTTPException(status_code=409, detail="Borrowing request is no longer pending")

    member = find_row("Members", "MID", transaction["MID"])
    book = find_row("Books", "BID", transaction["BID"])
    if not member or member.get("Status") != "Active":
        raise HTTPException(status_code=409, detail="Member is not active")
    if not book or book.get("Status") != "Active":
        raise HTTPException(status_code=409, detail="Book is not available")
    if int(book["AvailableCopies"]) <= 0:
        raise HTTPException(status_code=409, detail="No copy is available")

    active_count = sum(
        1 for loan in find_rows("BorrowList", "MID", transaction["MID"])
        if loan.get("Status") == "Approved"
    )
    if active_count >= MAX_ACTIVE_LOANS:
        raise HTTPException(status_code=409, detail="Maximum active loan limit reached")

    issue_date = date.today()
    due_date = issue_date + timedelta(days=LOAN_PERIOD_DAYS)
    update_row("BorrowList", "TID", tid, {
        "BDate": issue_date,
        "DueDate": due_date,
        "Status": "Approved",
    })
    update_row("Books", "BID", transaction["BID"], {
        "AvailableCopies": int(book["AvailableCopies"]) - 1
    })
    return {"TID": tid, "Status": "Approved", "DueDate": due_date.isoformat()}


@router.patch("/{tid}/reject")
def reject_borrowing(tid: str, account: Dict = Depends(require_librarian)) -> Dict:
    transaction = find_row("BorrowList", "TID", tid)
    if not transaction:
        raise HTTPException(status_code=404, detail="Borrowing transaction not found")
    if transaction.get("Status") != "Pending":
        raise HTTPException(status_code=409, detail="Borrowing request is no longer pending")
    update_row("BorrowList", "TID", tid, {"Status": "Rejected"})
    return {"TID": tid, "Status": "Rejected"}


@router.post("/{tid}/return")
def process_return(
    tid: str,
    request: ReturnRequest,
    account: Dict = Depends(require_librarian),
) -> Dict:
    transaction = find_row("BorrowList", "TID", tid)
    if not transaction:
        raise HTTPException(status_code=404, detail="Borrowing transaction not found")
    if transaction.get("Status") != "Approved":
        raise HTTPException(status_code=409, detail="Only approved loans can be returned")

    due_date = parse_date(transaction["DueDate"])
    if due_date is None:
        raise HTTPException(status_code=409, detail="Approved loan has no due date")
    if request.return_date < parse_date(transaction["BDate"]):
        raise HTTPException(status_code=422, detail="Return date cannot be before issue date")

    update_row("BorrowList", "TID", tid, {"RDate": request.return_date, "Status": "Returned"})
    book = find_row("Books", "BID", transaction["BID"])
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if int(book["AvailableCopies"]) >= int(book["TotalCopies"]):
        raise HTTPException(status_code=409, detail="Available copies cannot exceed total copies")
    update_row("Books", "BID", transaction["BID"], {
        "AvailableCopies": int(book["AvailableCopies"]) + 1
    })

    days_late = max(0, (request.return_date - due_date).days)
    fine = None
    if days_late > 0:
        from ..config import FINE_PER_DAY
        lid = next_id("LateList", "LID", "L")
        fine_due = days_late * FINE_PER_DAY
        append_row("LateList", {
            "LID": lid,
            "TID": tid,
            "DaysLate": days_late,
            "FineDue": fine_due,
            "AmountPaid": 0,
            "PaymentStatus": "Unpaid",
        })
        fine = find_row("LateList", "LID", lid)
    return {"TID": tid, "Status": "Returned", "DaysLate": days_late, "Fine": fine}


@router.get("/member/{mid}")
def member_loans(
    mid: str,
    account: Dict = Depends(get_current_account),
) -> list:
    if account.get("Role") != "Librarian" and str(account.get("MID", "")) != mid:
        raise HTTPException(status_code=403, detail="You may view only your own loans")
    return find_rows("BorrowList", "MID", mid)


@router.get("/overdue")
def overdue_loans(account: Dict = Depends(require_librarian)) -> list:
    today = date.today()
    overdue = []
    for loan in find_rows("BorrowList", "Status", "Approved"):
        due_date = parse_date(loan.get("DueDate"))
        if due_date and due_date < today:
            overdue.append({
                **loan,
                "DaysLate": (today - due_date).days,
            })
    return overdue
