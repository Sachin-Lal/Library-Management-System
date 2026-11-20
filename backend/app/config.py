from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WORKBOOK_PATH = DATA_DIR / "library_data.xlsx"
BACKUP_DIR = DATA_DIR / "backups"
JWT_SECRET = "library-management-development-secret-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 480

MAX_ACTIVE_LOANS = 3
LOAN_PERIOD_DAYS = 14
FINE_PER_DAY = 5
MEMBERSHIP_FEE = 100
MEMBERSHIP_DURATION_DAYS = 365
