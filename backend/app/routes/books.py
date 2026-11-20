from typing import Dict

from fastapi import APIRouter, Depends, HTTPException

from ..excel_handler import append_row, find_row, find_rows, next_id, update_row
from ..models import BookCreate, BookUpdate
from ..security import get_current_account, require_librarian


router = APIRouter(prefix="/books", tags=["Books"])


@router.get("")
def list_books(account: Dict = Depends(get_current_account)) -> list:
    return find_rows("Books", "Status", "Active")


@router.get("/search")
def search_books(query: str = "", account: Dict = Depends(get_current_account)) -> list:
    needle = query.lower()
    return [
        book for book in find_rows("Books", "Status", "Active")
        if needle in str(book.get("Name", "")).lower()
        or needle in str(book.get("Author", "")).lower()
    ]


@router.get("/{bid}")
def get_book(bid: str, account: Dict = Depends(get_current_account)) -> Dict:
    book = find_row("Books", "BID", bid)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("", status_code=201)
def create_book(request: BookCreate, account: Dict = Depends(require_librarian)) -> Dict:
    bid = next_id("Books", "BID", "B")
    append_row("Books", {
        "BID": bid,
        "Name": request.name,
        "Author": request.author,
        "Publisher": request.publisher,
        "TotalCopies": request.total_copies,
        "AvailableCopies": request.total_copies,
        "Status": "Active",
    })
    return find_row("Books", "BID", bid) or {}


@router.put("/{bid}")
def update_book(bid: str, request: BookUpdate, account: Dict = Depends(require_librarian)) -> Dict:
    book = find_row("Books", "BID", bid)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    changes = {}
    field_map = {"name": "Name", "author": "Author", "publisher": "Publisher", "total_copies": "TotalCopies"}
    for field, column in field_map.items():
        value = getattr(request, field)
        if value is not None:
            changes[column] = value
    if "TotalCopies" in changes:
        active_loans = sum(
            1 for loan in find_rows("BorrowList", "BID", bid)
            if loan.get("Status") == "Approved"
        )
        old_available = int(book["AvailableCopies"])
        old_total = int(book["TotalCopies"])
        new_total = int(changes["TotalCopies"])
        new_available = new_total - (old_total - old_available)
        if new_available < 0 or new_available > new_total:
            raise HTTPException(status_code=409, detail="Total copies would make availability invalid")
        changes["AvailableCopies"] = new_available
    updated = update_row("Books", "BID", bid, changes)
    return updated or {}


@router.delete("/{bid}")
def deactivate_book(bid: str, account: Dict = Depends(require_librarian)) -> Dict:
    book = find_row("Books", "BID", bid)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if any(loan.get("Status") == "Approved" for loan in find_rows("BorrowList", "BID", bid)):
        raise HTTPException(status_code=409, detail="Book cannot be deactivated while it has active loans")
    update_row("Books", "BID", bid, {"Status": "Inactive"})
    return {"BID": bid, "Status": "Inactive"}
