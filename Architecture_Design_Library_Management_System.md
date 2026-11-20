# Library Management System --- Architecture Design

**Frontend:** JavaFX\
**Backend:** Python FastAPI\
**Storage:** One Excel workbook (`library_data.xlsx`) with multiple
worksheets\
**Audience:** High-school-level educational project

## 1. Architecture Overview

The application uses a simple three-layer architecture:

1.  **Presentation layer --- JavaFX:** displays screens, collects user
    input and shows API responses.
2.  **Application layer --- FastAPI:** validates requests, checks
    permissions, applies library rules and coordinates data operations.
3.  **Data layer --- Excel:** stores books, members, accounts, borrowing
    transactions, registration requests and fines.

``` mermaid
flowchart TB
    L[Librarian] --> UI[JavaFX Desktop Application]
    M[Member] --> UI
    UI <-->|HTTP REST APIs / JSON| API[Python FastAPI]
    API --> AUTH[Authentication and Role Checks]
    API --> SVC[Library Business Services]
    AUTH --> SVC
    SVC --> EX[Excel Data Access Layer]
    EX <--> XLS[(library_data.xlsx)]
    XLS --- B[Books sheet]
    XLS --- MB[Members sheet]
    XLS --- TR[BorrowList sheet]
    XLS --- FI[LateList sheet]
    XLS --- AC[Accounts sheet]
    XLS --- RR[RegistrationRequests sheet]
```

### Main communication sequence

1.  A user performs an action in JavaFX.
2.  JavaFX sends an HTTP request to a FastAPI endpoint.
3.  FastAPI authenticates the user and checks their role.
4.  The relevant service applies business rules.
5.  The Excel data-access module reads or updates the workbook.
6.  FastAPI returns a JSON response.
7.  JavaFX updates the screen.

**Important:** JavaFX must not read or write the workbook directly. All
workbook operations go through FastAPI.

## 2. Suggested Technology Stack

  Area               Technology             Purpose
  ------------------ ---------------------- -------------------------------
  Desktop UI         JavaFX                 Screens and user interactions
  UI layout          FXML and CSS           Screen structure and styling
  Backend            Python                 Application logic
  API framework      FastAPI                REST endpoints
  Data validation    Pydantic               Validate request data
  Excel access       openpyxl               Read and write `.xlsx` files
  API testing        Swagger UI / Postman   Test backend endpoints
  Java HTTP client   Java `HttpClient`      Call FastAPI from Java
  Version control    Git and GitHub         Track source-code changes

## 3. Excel Workbook Design

Create one workbook named `library_data.xlsx`. Each worksheet acts like
a table. The first row of each sheet contains column names.

### 3.1 Books

  Column            Meaning
  ----------------- ------------------------------
  BID               Unique book ID (primary key)
  Name              Book title
  Author            Author name
  Publisher         Publisher name
  TotalCopies       Total copies owned
  AvailableCopies   Copies currently available
  Status            Active or Inactive

Example:

  ---------------------------------------------------------------------------------------
  BID       Name          Author    Publisher     TotalCopies   AvailableCopies Status
  --------- ------------- --------- ----------- ------------- ----------------- ---------
  B001      Python Basics John      ABC Press               5                 3 Active
                          Smith                                                 

  B002      Java          Jane Doe  Learning                3                 2 Active
            Programming             House                                       
  ---------------------------------------------------------------------------------------

### 3.2 Members

  Column       Meaning
  ------------ --------------------------------
  MID          Unique member ID (primary key)
  FName        First name
  LName        Last name
  Phone        Contact number
  Email        Email address
  Address      Residential address
  JoinDate     Membership start date
  ExpiryDate   Membership expiry date
  Status       Pending, Active or Inactive

### 3.3 BorrowList

This sheet stores borrowing requests and approved loans. A row starts as
a pending request and changes status as the librarian processes it.

  Column        Meaning
  ------------- ------------------------------------------------
  TID           Unique transaction ID (primary key)
  MID           Member ID (foreign key)
  BID           Book ID (foreign key)
  BDate         Date the book was issued; blank until approved
  DueDate       Expected return date; blank until approved
  RDate         Actual return date; blank until returned
  Status        Pending, Approved, Rejected or Returned
  RequestDate   Date the member submitted the request

### 3.4 LateList

  Column          Meaning
  --------------- --------------------------------------
  LID             Unique fine ID (primary key)
  TID             Related transaction ID (foreign key)
  DaysLate        Number of overdue days
  FineDue         Total fine calculated
  AmountPaid      Total amount paid
  PaymentStatus   Unpaid, Partial or Paid

### 3.5 Accounts

  Column         Meaning
  -------------- ---------------------------------------
  UID            Unique account ID (primary key)
  Username       Login username
  PasswordHash   Secure password hash
  Role           Librarian or Member
  MID            Linked member ID; blank for librarian
  Status         Active or Inactive

The librarian account can be created during initial setup. A member
account is created after the librarian approves the member's
registration.

### 3.6 RegistrationRequests

  Column              Meaning
  ------------------- ----------------------------------------------
  RID                 Unique registration request ID (primary key)
  FName               First name
  LName               Last name
  Phone               Contact number
  Email               Email address
  Address             Address
  RequestDate         Submission date
  MembershipPayment   Amount recorded as paid
  Status              Pending, Approved or Rejected

For this learning version, membership payments are recorded manually. Do
not store payment-card details.

## 4. Table Relationships

``` mermaid
erDiagram
    MEMBERS ||--o{ BORROWLIST : makes
    BOOKS ||--o{ BORROWLIST : appears_in
    BORROWLIST ||--o{ LATELIST : may_generate
    MEMBERS ||--o| ACCOUNTS : has
    MEMBERS {
        string MID PK
        string FName
        string LName
        string Phone
        string Email
        string Address
        string Status
    }
    BOOKS {
        string BID PK
        string Name
        string Author
        string Publisher
        int TotalCopies
        int AvailableCopies
        string Status
    }
    BORROWLIST {
        string TID PK
        string MID FK
        string BID FK
        date BDate
        date DueDate
        date RDate
        string Status
    }
    LATELIST {
        string LID PK
        string TID FK
        int DaysLate
        decimal FineDue
        decimal AmountPaid
        string PaymentStatus
    }
    ACCOUNTS {
        string UID PK
        string Username
        string PasswordHash
        string Role
        string MID FK
    }
```

-   `MID` connects a member to their borrowing transactions.
-   `BID` connects a book to borrowing transactions.
-   `TID` connects a borrowing transaction to a fine record.
-   `MID` connects a member to their login account.

A primary key uniquely identifies a row. A foreign key stores the ID of
a related row in another sheet.

## 5. Backend Module Design

Suggested backend structure:

``` text
backend/
├── main.py
├── requirements.txt
├── routes/
│   ├── auth.py
│   ├── members.py
│   ├── books.py
│   ├── borrowing.py
│   └── fines.py
├── services/
│   ├── member_service.py
│   ├── book_service.py
│   ├── borrowing_service.py
│   └── fine_service.py
├── models/
│   ├── member.py
│   ├── book.py
│   └── transaction.py
└── database/
    ├── excel_handler.py
    └── library_data.xlsx
```

### Responsibilities

-   `main.py`: creates the FastAPI application and registers routers.
-   `routes/`: defines HTTP endpoints and receives requests.
-   `services/`: contains business rules and workflows.
-   `models/`: defines Pydantic request and response models.
-   `excel_handler.py`: performs workbook reads and writes.
-   `library_data.xlsx`: stores the project data.

Keep business rules in the service layer. Keep Excel-specific code in
the data-access layer.

## 6. API Design

All endpoints use JSON for request and response bodies.

### Authentication

  Method   Endpoint           Purpose
  -------- ------------------ -----------------------------
  POST     `/auth/login`      Log in
  POST     `/auth/register`   Submit registration request
  GET      `/auth/me`         Get current user's details

### Members

  Method   Endpoint                  Purpose
  -------- ------------------------- --------------------------
  GET      `/members`                List members (Librarian)
  GET      `/members/{mid}`          Get member details
  POST     `/members`                Add member (Librarian)
  PUT      `/members/{mid}`          Update member details
  PATCH    `/members/{mid}/status`   Change membership status

### Registration requests

  Method   Endpoint                         Purpose
  -------- -------------------------------- ---------------------------
  GET      `/registrations`                 List requests (Librarian)
  PATCH    `/registrations/{rid}/approve`   Approve request
  PATCH    `/registrations/{rid}/reject`    Reject request

### Books

  Method   Endpoint          Purpose
  -------- ----------------- -----------------------------
  GET      `/books`          List books
  GET      `/books/{bid}`    Get book details
  GET      `/books/search`   Search by title or author
  POST     `/books`          Add book (Librarian)
  PUT      `/books/{bid}`    Update book (Librarian)
  DELETE   `/books/{bid}`    Deactivate book (Librarian)

### Borrowing

  Method   Endpoint                  Purpose
  -------- ------------------------- --------------------------------
  POST     `/borrow/request`         Submit a borrowing request
  GET      `/borrow/requests`        List requests (Librarian)
  PATCH    `/borrow/{tid}/approve`   Approve request (Librarian)
  PATCH    `/borrow/{tid}/reject`    Reject request (Librarian)
  POST     `/borrow/{tid}/return`    Process return (Librarian)
  GET      `/borrow/member/{mid}`    View member's loans
  GET      `/borrow/overdue`         List overdue loans (Librarian)

### Fines

  Method   Endpoint                Purpose
  -------- ----------------------- ------------------------------
  GET      `/fines`                List fines (Librarian)
  GET      `/fines/member/{mid}`   View member's fines
  POST     `/fines/calculate`      Calculate fine
  PATCH    `/fines/{lid}/pay`      Record a payment (Librarian)

Every endpoint must check that the logged-in user has permission to
perform the requested action. Hiding a button in JavaFX is not
sufficient security.

## 7. Important Workflows

### 7.1 Member registration

``` mermaid
flowchart TD
    A[Member fills registration form] --> B[Backend validates details]
    B --> C{Details valid?}
    C -- No --> D[Return validation error]
    C -- Yes --> E[Save Pending registration request]
    E --> F[Librarian reviews request]
    F --> G{Approve?}
    G -- No --> H[Mark request Rejected]
    G -- Yes --> I[Create Member ID and account]
    I --> J[Mark membership Active]
```

### 7.2 Book borrowing

``` mermaid
flowchart TD
    A[Member selects a book] --> B[Check membership]
    B --> C{Active member?}
    C -- No --> D[Reject request]
    C -- Yes --> E[Check available copies]
    E --> F{Copy available?}
    F -- No --> G[Show unavailable message]
    F -- Yes --> H[Save Pending request]
    H --> I[Librarian reviews request]
    I --> J{Approve?}
    J -- No --> K[Mark Rejected]
    J -- Yes --> L[Create approved loan]
    L --> M[Decrease AvailableCopies by 1]
    M --> N[Set issue date and due date]
```

### 7.3 Book return and fine calculation

``` mermaid
flowchart TD
    A[Librarian selects active loan] --> B[Enter return date]
    B --> C[Calculate overdue days]
    C --> D{Returned after due date?}
    D -- No --> E[Fine is zero]
    D -- Yes --> F[Calculate fine]
    E --> G[Mark transaction Returned]
    F --> G
    G --> H[Increase AvailableCopies by 1]
    H --> I[Save fine record if required]
    I --> J[Show updated loan and fine status]
```

### Fine formula

`DaysLate = max(0, ReturnDate - DueDate)`

`FineDue = DaysLate × FinePerDay`

For a book that has not been returned, use today's date instead of the
return date.

Example: If the due date is 1 November, the return date is 5 November
and the daily fine is ₹5, then the member is four days late and owes
₹20.

## 8. Frontend Structure

Suggested JavaFX project structure:

``` text
frontend/
├── src/
│   ├── controllers/
│   │   ├── LoginController.java
│   │   ├── LibrarianController.java
│   │   ├── MemberController.java
│   │   ├── BookController.java
│   │   └── BorrowController.java
│   ├── services/
│   │   └── ApiService.java
│   ├── models/
│   │   ├── Book.java
│   │   ├── Member.java
│   │   └── Transaction.java
│   └── views/
│       ├── login.fxml
│       ├── librarian.fxml
│       └── member.fxml
└── pom.xml
```

JavaFX screens should include:

-   Login screen.
-   Member registration screen.
-   Librarian dashboard.
-   Member dashboard.
-   Book catalogue and search.
-   Member management.
-   Registration request list.
-   Borrowing request list.
-   Current loans and return screen.
-   Fine and payment screen.

`ApiService.java` should centralize HTTP communication with FastAPI.
Controllers should call this service instead of repeating HTTP request
code.

## 9. Error Handling and Data Validation

Examples of checks:

-   Reject empty book titles and member names.
-   Reject duplicate IDs, usernames and email addresses.
-   Reject a borrowing request from an inactive member.
-   Reject a request when no copies are available.
-   Reject a return for a transaction that is not currently approved.
-   Prevent available copies from becoming negative.
-   Prevent available copies from exceeding total copies.
-   Reject a fine payment larger than the remaining amount, unless
    overpayments are explicitly supported.
-   Return clear HTTP error codes and messages.

## 10. Excel-Specific Safety Rules

Excel is suitable for this small learning project, but it is not a full
database.

1.  Only the backend should access the workbook.
2.  Protect write operations with a lock so two requests do not update
    the file simultaneously.
3.  Create a backup before important updates.
4.  Validate IDs and related records before writing.
5.  Save updates carefully and handle file errors.
6.  Avoid deleting historical borrowing and payment records.
7.  Keep the workbook closed in spreadsheet applications while the
    backend is writing to it.
8.  Test that data remains correct after restarting the backend.

For this project, use one backend process. A production system with many
users should use a database such as SQLite or PostgreSQL instead of
Excel.

## 11. Security Basics

-   Hash passwords with a suitable password-hashing library.
-   Never store plain-text passwords.
-   Require authentication for protected endpoints.
-   Check roles on the backend for every protected operation.
-   A Member may access only their own member-specific records.
-   A Librarian may access librarian management operations.
-   Do not store payment-card numbers or sensitive payment credentials.

## 12. Deployment and Running Locally

During development:

1.  Start the FastAPI server on the local machine.
2.  Confirm that the API documentation opens at `/docs`.
3.  Run the JavaFX application.
4.  Configure the Java API client to use the local FastAPI base URL.
5.  Keep the workbook in the backend data directory.
6.  Test the application with sample librarian and member accounts.

## 13. Known Limitations

-   Excel does not provide database transactions, indexing or safe
    multi-user writes.
-   A file lock reduces write conflicts but does not make Excel
    equivalent to a database.
-   The project is intended for learning and demonstration.
-   If the application grows, replace the Excel data layer with SQLite
    or PostgreSQL while keeping most API and frontend responsibilities
    similar.
