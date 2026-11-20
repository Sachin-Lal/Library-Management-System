# Library Management System

A learning desktop-library application using JavaFX, Python FastAPI, and one Excel workbook.

## Backend

### Requirements

- Python 3.10 or newer
- Excel support through `openpyxl`

### Setup

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "."
uvicorn app.main:app --reload
```

Open Swagger UI at `http://127.0.0.1:8000/docs`.

The first server start creates `backend/data/library_data.xlsx`, a backup directory, sample books, and these accounts:

| Role | Username | Password |
|---|---|---|
| Librarian | `admin` | `admin123` |
| Member | `member` | `member123` |

## Tests

From the repository root:

```powershell
$env:PYTHONPATH = "backend"
python -m pytest backend/tests -q
```

## API Authentication

Protected endpoints require a bearer token returned by `POST /auth/login`:

```text
Authorization: Bearer <access-token>
```

## Workbook

Only the backend may read or write `backend/data/library_data.xlsx`. Important writes create timestamped backups in `backend/data/backups`.
