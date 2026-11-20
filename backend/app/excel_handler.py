import shutil
import threading
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from openpyxl import Workbook, load_workbook

from .config import BACKUP_DIR, WORKBOOK_PATH


SheetRow = Dict[str, Any]

HEADERS = {
    "Books": ["BID", "Name", "Author", "Publisher", "TotalCopies", "AvailableCopies", "Status"],
    "Members": ["MID", "FName", "LName", "Phone", "Email", "Address", "JoinDate", "ExpiryDate", "Status"],
    "BorrowList": ["TID", "MID", "BID", "BDate", "DueDate", "RDate", "Status", "RequestDate"],
    "LateList": ["LID", "TID", "DaysLate", "FineDue", "AmountPaid", "PaymentStatus"],
    "Accounts": ["UID", "Username", "PasswordHash", "Role", "MID", "Status"],
    "RegistrationRequests": [
        "RID", "FName", "LName", "Phone", "Email", "Address", "RequestDate",
        "MembershipPayment", "Status", "Username", "PasswordHash",
    ],
}

_write_lock = threading.RLock()


def _serialize(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _deserialize(value: Any) -> Any:
    return value


def initialize_workbook() -> None:
    WORKBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if WORKBOOK_PATH.exists():
        return

    workbook = Workbook()
    workbook.remove(workbook.active)
    for sheet_name, headers in HEADERS.items():
        sheet = workbook.create_sheet(sheet_name)
        sheet.append(headers)

    from .security import hash_password

    sheet = workbook["Accounts"]
    sheet.append(["U001", "admin", hash_password("admin123"), "Librarian", "", "Active"])

    today = date.today()
    expiry = date.fromordinal(today.toordinal() + 365)
    workbook["Books"].append(["B001", "Python Basics", "John Smith", "ABC Press", 5, 5, "Active"])
    workbook["Books"].append(["B002", "Java Programming", "Jane Doe", "Learning House", 3, 3, "Active"])
    workbook["Members"].append(["M001", "Demo", "Member", "9999999999", "member@example.com", "Demo Address", today, expiry, "Active"])
    workbook["Accounts"].append(["U002", "member", hash_password("member123"), "Member", "M001", "Active"])

    workbook.save(WORKBOOK_PATH)


def backup_workbook() -> Optional[Path]:
    if not WORKBOOK_PATH.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    destination = BACKUP_DIR / f"library_data-{timestamp}.xlsx"
    shutil.copy2(WORKBOOK_PATH, destination)
    return destination


def _rows(sheet_name: str) -> List[SheetRow]:
    initialize_workbook()
    workbook = load_workbook(WORKBOOK_PATH)
    sheet = workbook[sheet_name]
    headers = [cell.value for cell in sheet[1]]
    rows: List[SheetRow] = []
    for cells in sheet.iter_rows(min_row=2, values_only=True):
        if not any(value not in (None, "") for value in cells):
            continue
        rows.append({headers[index]: _deserialize(cells[index]) for index in range(len(headers))})
    workbook.close()
    return rows


def read_rows(sheet_name: str) -> List[SheetRow]:
    with _write_lock:
        return _rows(sheet_name)


def find_row(sheet_name: str, column: str, value: Any) -> Optional[SheetRow]:
    for row in read_rows(sheet_name):
        if str(row.get(column, "")) == str(value):
            return row
    return None


def find_rows(sheet_name: str, column: str, value: Any) -> List[SheetRow]:
    return [row for row in read_rows(sheet_name) if str(row.get(column, "")) == str(value)]


def parse_date(value: Any) -> Optional[date]:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def next_id(sheet_name: str, id_column: str, prefix: str) -> str:
    rows = read_rows(sheet_name)
    numbers = []
    for row in rows:
        raw = str(row.get(id_column, ""))
        if raw.startswith(prefix):
            suffix = raw[len(prefix):]
            if suffix.isdigit():
                numbers.append(int(suffix))
    number = max(numbers, default=0) + 1
    return f"{prefix}{number:03d}"


def append_row(sheet_name: str, row: Dict[str, Any], backup: bool = True) -> SheetRow:
    with _write_lock:
        initialize_workbook()
        if backup:
            backup_workbook()
        workbook = load_workbook(WORKBOOK_PATH)
        sheet = workbook[sheet_name]
        headers = [cell.value for cell in sheet[1]]
        sheet.append([_serialize(row.get(header)) for header in headers])
        workbook.save(WORKBOOK_PATH)
        workbook.close()
        return row


def update_row(sheet_name: str, id_column: str, id_value: str, changes: Dict[str, Any], backup: bool = True) -> Optional[SheetRow]:
    with _write_lock:
        initialize_workbook()
        workbook = load_workbook(WORKBOOK_PATH)
        sheet = workbook[sheet_name]
        headers = [cell.value for cell in sheet[1]]
        for row_number in range(2, sheet.max_row + 1):
            if str(sheet.cell(row=row_number, column=headers.index(id_column) + 1).value) != str(id_value):
                continue
            if backup:
                backup_workbook()
            for column_name, value in changes.items():
                if column_name not in headers:
                    raise ValueError(f"Unknown column {column_name}")
                sheet.cell(row=row_number, column=headers.index(column_name) + 1).value = _serialize(value)
            workbook.save(WORKBOOK_PATH)
            workbook.close()
            updated = find_row(sheet_name, id_column, id_value)
            return updated
        workbook.close()
        return None
