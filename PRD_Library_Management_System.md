# Library Management System --- Product Requirements Document (PRD)

**Project type:** Educational / high-school-level software project\
**Frontend:** JavaFX (assuming "JavaUX" means JavaFX)\
**Backend:** Python with FastAPI\
**Data storage:** One Excel workbook with separate worksheets\
**User roles:** Librarian and Member

## 1. Project Overview

The Library Management System (LMS) is a desktop application for
managing a small library. It supports two types of users:

-   **Librarian:** manages members, books, borrowing requests, returns
    and late fees.
-   **Member:** registers for membership, searches for books, requests
    borrowing, returns books and checks outstanding late fees.

The JavaFX frontend communicates with the Python FastAPI backend through
HTTP REST APIs. The backend reads and writes data in an Excel workbook.
The frontend must not access the Excel workbook directly.

## 2. Project Goals

1.  Build a simple, usable desktop application.
2.  Learn frontend-to-backend communication using REST APIs.
3.  Practise CRUD operations (Create, Read, Update and Delete).
4.  Understand tables, primary keys and foreign keys.
5.  Implement role-based access for Librarians and Members.
6.  Implement a complete book borrowing and return workflow.
7.  Calculate and record late fees.

## 3. Scope

### Included in the first version

-   Login for Librarians and Members.
-   Member registration and membership cancellation.
-   Librarian approval of registration requests.
-   Member listing and member status management.
-   Book catalogue, search and availability.
-   Add, update and deactivate books.
-   Borrowing requests and librarian approval/rejection.
-   Return processing and borrowing history.
-   Overdue book list.
-   Late-fee calculation and payment recording.
-   Excel workbook storage.

### Not included in the first version

-   Online payment gateway.
-   Barcode or RFID scanning.
-   Email or SMS notifications.
-   Multiple library branches.
-   Cloud-hosted database.
-   Mobile application.

## 4. User Roles and Features

### 4.1 Librarian

**Members** - View the member list and member details. - Add a member
when required. - Review and approve or reject registration requests. -
Deactivate a member or revoke membership. - View membership status.

**Books** - View all books and their availability. - Add new books. -
Update book details and copy counts. - Deactivate books that are no
longer part of the collection. - Prevent removal of a book while it has
active loans.

**Borrowing** - View pending borrowing requests. - Approve or reject
requests. - View current and past borrowing transactions. - Process
returned books. - View overdue books.

**Late fees** - View outstanding fines. - Review the fine associated
with a borrowing transaction. - Record full or partial payments. - View
payment status.

### 4.2 Member

**Membership** - Submit a membership registration request. - Provide
name, phone number, email and address. - View registration status. -
Request membership cancellation.

**Books** - Browse and search the book catalogue. - View book
availability. - Request to borrow an available book. - View current
loans and borrowing history. - Return a book through the library's
return process.

**Late fees** - View outstanding late fees. - View the number of overdue
days and amount due. - View recorded payment status.

> For the first version, membership and fine payments are recorded by
> the librarian. No real payment gateway is required.

## 5. Functional Requirements

  ID      Requirement                                     User
  ------- ----------------------------------------------- -----------
  FR-01   Log in to the application                       Both
  FR-02   Submit a membership registration request        Member
  FR-03   View and approve/reject registration requests   Librarian
  FR-04   View member list and member details             Librarian
  FR-05   Add, update or deactivate a member              Librarian
  FR-06   View the book catalogue                         Both
  FR-07   Add, update or deactivate books                 Librarian
  FR-08   Search books and check availability             Member
  FR-09   Submit a borrowing request                      Member
  FR-10   Approve or reject a borrowing request           Librarian
  FR-11   Process a book return                           Librarian
  FR-12   View borrowing history                          Both
  FR-13   View overdue books                              Librarian
  FR-14   Calculate late fees                             Backend
  FR-15   View outstanding fines                          Both
  FR-16   Record a fine payment                           Librarian
  FR-17   Request membership cancellation                 Member
  FR-18   View a library summary/dashboard                Librarian

## 6. Business Rules

These are proposed starter rules. The project team can change the values
after discussing them with the teacher or project guide.

1.  Only an approved, active member may borrow a book.
2.  A member cannot request a book when no copy is available.
3.  A borrowing request must be approved by a librarian before it
    becomes an active loan.
4.  Approval must reduce the book's available-copy count by one.
5.  Returning a book must increase its available-copy count by one.
6.  Each borrowing transaction must have a unique transaction ID.
7.  The due date is calculated from the approval/issue date and the
    configured loan period.
8.  A late fee is calculated only for days after the due date.
9.  A member with an unpaid fine may be prevented from making another
    borrowing request. This is a configurable project rule.
10. A member with active loans cannot complete membership cancellation
    until the books are returned.
11. A book with an active loan cannot be deactivated.
12. Historical transactions and payments must be retained. Deactivate
    records instead of deleting history.
13. A request that is rejected must not change the available-copy count.
14. A request that is still pending must not change the available-copy
    count.

## 7. Initial Configurable Policies

  Policy                              Example starting value
  --------------------------------- ------------------------
  Maximum active loans per member                          3
  Loan period                                        14 days
  Late fee per day                                        ₹5
  Membership fee                                        ₹100
  Membership duration                                 1 year

These are example values for the learning project, not fixed
requirements. Store configurable values in one place rather than
scattering them throughout the code.

## 8. Data Requirements

The application will use a single Excel workbook named
`library_data.xlsx`, containing these worksheets:

1.  `Books`
2.  `Members`
3.  `BorrowList` (borrowing transactions and request statuses)
4.  `LateList` (fine records)
5.  `Accounts` (login details and roles)
6.  `RegistrationRequests`

Detailed columns and relationships are documented in
`ARCHITECTURE_DESIGN.md`.

## 9. Non-Functional Requirements

-   The interface should be simple and understandable for first-time
    users.
-   Backend APIs must validate input before changing data.
-   Backend endpoints must enforce user roles and permissions.
-   Passwords must be stored as hashes, not plain text.
-   The application must show understandable success and error messages.
-   IDs must be unique.
-   Excel writes must be protected against simultaneous updates.
-   The backend should create backups before important workbook updates.
-   The application should retain transaction and payment history.
-   The code should be divided into understandable modules.

## 10. Acceptance Criteria

The first version is considered complete when:

-   A librarian and a member can log in with the correct role.
-   A member can submit a registration request.
-   A librarian can approve or reject that request.
-   A member can search for books and submit a borrowing request.
-   A librarian can approve or reject a borrowing request.
-   An approved loan updates book availability correctly.
-   A librarian can process a return.
-   The backend calculates an overdue fine correctly.
-   A librarian can record a fine payment.
-   Members cannot access librarian-only operations.
-   Data remains present in the Excel workbook after the backend
    restarts.

## 11. Assumptions and Limitations

-   "JavaUX" is interpreted as JavaFX. Confirm this before
    implementation if a different frontend technology was intended.
-   Excel is being used as a learning substitute for a database.
-   The first version is intended for a small demonstration, not a
    production library.
-   A single backend process should control workbook writes.
-   Real online payments are outside the project scope.
