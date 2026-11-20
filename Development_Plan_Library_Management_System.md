# Library Management System --- Task-wise Development Plan

**Project level:** High-school educational activity\
**Suggested duration:** 4 weeks\
**Suggested daily effort:** 1--2 hours\
**Frontend:** JavaFX\
**Backend:** Python FastAPI\
**Storage:** Excel workbook with separate worksheets

## 1. How to Use This Plan

Build the project in small steps. Complete and test one task before
moving to the next. The backend should work independently before the
team connects the JavaFX frontend.

Each task includes an expected result so students and teachers can check
progress.

## 2. Four-Week Overview

  -----------------------------------------------------------------------
  Week                    Focus                   Main outcome
  ----------------------- ----------------------- -----------------------
  Week 1                  Planning and backend    FastAPI can read and
                          foundation              write Excel data

  Week 2                  Backend features        Core library workflows
                                                  work through APIs

  Week 3                  JavaFX frontend         Screens are built and
                                                  can call APIs

  Week 4                  Integration and testing Complete working
                                                  demonstration
  -----------------------------------------------------------------------

## 3. Week 1 --- Planning and Backend Foundation

**Goal:** Understand the requirements, prepare tools and create the
first working API.

  ----------------------------------------------------------------------------
  Task ID           Task              Steps                  Expected result
  ----------------- ----------------- ---------------------- -----------------
  W1-T01            Understand        Read the PRD; identify Students can
                    requirements      Librarian and Member   explain what the
                                      features; list the     application must
                                      main workflows.        do.

  W1-T02            Install tools     Install Python, a Java Development
                                      JDK, an IDE, Git and a environment is
                                      JavaFX-compatible      ready.
                                      project setup.         

  W1-T03            Create project    Create separate        Project structure
                    folders           `frontend` and         exists.
                                      `backend` folders.     

  W1-T04            Create Excel      Create                 Workbook has all
                    workbook          `library_data.xlsx`    required sheets
                                      and the Books,         and headers.
                                      Members, BorrowList,   
                                      LateList, Accounts and 
                                      RegistrationRequests   
                                      sheets.                

  W1-T05            Add sample        Add a few sample books Workbook contains
                    records           and members with       test data.
                                      unique IDs.            

  W1-T06            Set up Python     Create a virtual       Python
                    environment       environment and        dependencies are
                                      install FastAPI,       installed.
                                      Uvicorn and openpyxl.  

  W1-T07            Create first      Create `main.py`; add  Server starts
                    FastAPI app       a simple root          successfully.
                                      endpoint; run the      
                                      server.                

  W1-T08            Read Excel data   Write a helper         Python can read
                                      function that loads    the workbook.
                                      book rows from the     
                                      Books sheet.           

  W1-T09            Create first GET  Create `GET /books`    Swagger UI
                    endpoint          and return book        displays the book
                                      records as JSON.       list.

  W1-T10            Test the endpoint Open `/docs`; call the First API is
                                      endpoint; test with    tested.
                                      empty and populated    
                                      sheets.                
  ----------------------------------------------------------------------------

**Week 1 checkpoint:** Demonstrate that `GET /books` returns records
stored in the Excel workbook.

## 4. Week 2 --- Backend Development

**Goal:** Implement validation, user management and library workflows.

  --------------------------------------------------------------------------
  Task ID           Task                 Steps             Expected result
  ----------------- -------------------- ----------------- -----------------
  W2-T01            Create Pydantic      Define request    API input has
                    models               models for books, defined fields
                                         members, login    and validation.
                                         and borrowing.    

  W2-T02            Build Excel write    Add functions to  Backend can
                    functions            append, update    perform basic
                                         and find rows by  CRUD operations.
                                         ID.               

  W2-T03            Implement book APIs  Add list, search, Book management
                                         add, update and   works through
                                         deactivate        APIs.
                                         operations.       

  W2-T04            Implement member     Add list,         Member management
                    APIs                 details, add,     works through
                                         update and status APIs.
                                         operations.       

  W2-T05            Implement            Save a new        Registration
                    registration         member's          request is
                                         registration      stored.
                                         request with      
                                         Pending status.   

  W2-T06            Implement            Allow a Librarian Registration
                    approval/rejection   to approve or     workflow works.
                                         reject a request. 
                                         Create member and 
                                         account records   
                                         on approval.      

  W2-T07            Implement            Verify login      Librarian and
                    authentication       details and       Member logins
                                         return            work.
                                         authenticated     
                                         user information  
                                         and role.         

  W2-T08            Add role checks      Protect           Users cannot
                                         librarian-only    perform
                                         endpoints and     unauthorized
                                         member-specific   actions.
                                         records.          

  W2-T09            Implement borrowing  Check active      Member can
                    request              membership and    request an
                                         availability;     available book.
                                         create a Pending  
                                         request.          

  W2-T10            Implement            Approve or reject Librarian can
                    approval/rejection   pending requests; process requests
                                         update copy count correctly.
                                         only on approval. 

  W2-T11            Implement returns    Validate active   Return workflow
                                         loan; record      works.
                                         return date;      
                                         increase          
                                         available copies. 

  W2-T12            Implement late-fee   Calculate overdue Late fees are
                    calculation          days and amount   calculated
                                         using the         correctly.
                                         configured daily  
                                         rate.             

  W2-T13            Implement payment    Record full or    Payment records
                    recording            partial payments  are stored.
                                         and update        
                                         payment status.   

  W2-T14            Test backend         Test successful,  Core APIs pass
                    workflows            invalid and       manual tests.
                                         unauthorized      
                                         requests in       
                                         Swagger UI or     
                                         Postman.          
  --------------------------------------------------------------------------

**Week 2 checkpoint:** Demonstrate registration, librarian approval,
borrowing, return and fine calculation using API calls only.

## 5. Week 3 --- JavaFX Frontend Development

**Goal:** Create the desktop screens and connect JavaFX to the backend.

  -----------------------------------------------------------------------
  Task ID           Task              Steps             Expected result
  ----------------- ----------------- ----------------- -----------------
  W3-T01            Create JavaFX     Create the Java   Desktop
                    project           project and add   application
                                      JavaFX            opens.
                                      dependencies.     

  W3-T02            Create login      Add username and  Login screen is
                    screen            password fields   visible.
                                      and a login       
                                      button.           

  W3-T03            Create API        Use Java          JavaFX can
                    service           `HttpClient` to   communicate with
                                      send requests to  the backend.
                                      FastAPI;          
                                      centralize the    
                                      base URL and      
                                      request logic.    

  W3-T04            Connect login     Call              Login uses real
                                      `/auth/login`;    backend data.
                                      handle success    
                                      and failure       
                                      responses.        

  W3-T05            Create Librarian  Add navigation    Librarian can
                    dashboard         for Members,      navigate the
                                      Books, Borrowing  application.
                                      and Fines.        

  W3-T06            Create Member     Add navigation    Member can
                    dashboard         for Catalogue, My navigate the
                                      Loans,            application.
                                      Registration and  
                                      Fines.            

  W3-T07            Create book       Display books in  Member can browse
                    catalogue         a table; add      books.
                                      search and        
                                      availability      
                                      information.      

  W3-T08            Create book       Add book form and Librarian can
                    management screen edit/deactivate   manage books.
                                      actions.          

  W3-T09            Create member     Display member    Librarian can
                    management screen records and       view and manage
                                      membership        members.
                                      status.           

  W3-T10            Create            Add member detail Member can submit
                    registration      fields and submit a registration
                    screen            action.           request.

  W3-T11            Create borrowing  Show requests and Librarian can
                    screen            allow librarian   process requests.
                                      approval or       
                                      rejection.        

  W3-T12            Create returns    Display active    Librarian can
                    and fines screens loans, overdue    process returns
                                      details and       and record
                                      payment actions.  payments.

  W3-T13            Display API       Show useful       UI handles errors
                    errors            messages when the clearly.
                                      backend rejects a 
                                      request or is     
                                      unavailable.      
  -----------------------------------------------------------------------

**Week 3 checkpoint:** Demonstrate JavaFX login, dashboards and book
catalogue using live FastAPI responses.

## 6. Week 4 --- Integration, Testing and Finalization

**Goal:** Connect every screen, test the complete application and
prepare the demonstration.

  -----------------------------------------------------------------------
  Task ID           Task              Steps             Expected result
  ----------------- ----------------- ----------------- -----------------
  W4-T01            Integrate all     Connect forms,    Main application
                    screens           tables and        features work end
                                      buttons to the    to end.
                                      relevant APIs.    

  W4-T02            Test registration Submit a request  Registration
                                      and               status changes
                                      approve/reject it correctly.
                                      as Librarian.     

  W4-T03            Test book         Add, search,      Book records
                    management        update and        remain correct.
                                      deactivate books. 

  W4-T04            Test borrowing    Request a book    Status and
                                      and               available-copy
                                      approve/reject    count are
                                      it.               correct.

  W4-T05            Test returns      Return an active  Return is
                                      loan and verify   recorded exactly
                                      the book count.   once.

  W4-T06            Test fines        Test on-time and  Fine calculations
                                      late returns;     are correct.
                                      compare           
                                      calculated values 
                                      with manual       
                                      calculations.     

  W4-T07            Test payments     Record full and   Amount paid and
                                      partial payments. payment status
                                                        are correct.

  W4-T08            Test access       Try Member access Unauthorized
                    control           to librarian-only access is
                                      features and      blocked.
                                      another member's  
                                      records.          

  W4-T09            Test invalid data Try blank fields, Backend rejects
                                      duplicate IDs,    invalid
                                      unavailable books operations
                                      and invalid       safely.
                                      transaction IDs.  

  W4-T10            Test Excel        Restart backend;  Data remains
                    consistency       inspect workbook; consistent.
                                      verify IDs,       
                                      relationships and 
                                      counts.           

  W4-T11            Add backup        Create a backup   A recovery copy
                    handling          before important  is available.
                                      workbook updates. 

  W4-T12            Prepare           Complete README,  Project can be
                    documentation     setup             understood and
                                      instructions, API run by another
                                      list,             student.
                                      architecture and  
                                      test cases.       

  W4-T13            Prepare           Create sample     Final
                    demonstration     accounts and      demonstration is
                                      data; rehearse    ready.
                                      one complete      
                                      workflow.         
  -----------------------------------------------------------------------

**Week 4 checkpoint:** Demonstrate a complete journey: registration →
approval → book request → approval → return → fine calculation/payment.

## 7. Suggested Task Dependencies

Some tasks depend on earlier tasks. Follow this order:

``` mermaid
flowchart TD
    A[Requirements and project setup] --> B[Excel workbook]
    B --> C[Excel read/write helper]
    C --> D[FastAPI book and member APIs]
    D --> E[Authentication and registration]
    E --> F[Borrowing and return workflows]
    F --> G[Fine calculation and payments]
    G --> H[Backend testing]
    H --> I[JavaFX project and API client]
    I --> J[Login and dashboards]
    J --> K[Connect feature screens]
    K --> L[End-to-end testing]
    L --> M[Documentation and demonstration]
```

## 8. Testing Checklist

Use these test cases before declaring the project complete.

  Test ID   Scenario                              Expected result
  --------- ------------------------------------- ------------------------------------------
  TC-01     Correct login credentials             Login succeeds
  TC-02     Incorrect password                    Login fails with a clear message
  TC-03     New member registration               Pending request is created
  TC-04     Librarian approves request            Member and account are created
  TC-05     Add a book                            Book appears in catalogue
  TC-06     Search by title or author             Matching books are shown
  TC-07     Request an available book             Pending request is created
  TC-08     Request an unavailable book           Request is rejected
  TC-09     Approve borrowing                     Available copies decrease by one
  TC-10     Reject borrowing                      Available copies do not change
  TC-11     Return on or before due date          No late fee is charged
  TC-12     Return after due date                 Late fee is calculated correctly
  TC-13     Record a payment                      Amount paid and status update
  TC-14     Member calls librarian-only API       Access is denied
  TC-15     Deactivate book with an active loan   Operation is rejected
  TC-16     Restart backend                       Existing workbook data remains available

## 9. Final Deliverables

Students should submit:

1.  JavaFX frontend source code.
2.  Python FastAPI backend source code.
3.  `library_data.xlsx` with sample data.
4.  README with installation and run instructions.
5.  API endpoint documentation.
6.  Architecture diagram or architecture document.
7.  Test-case results.
8.  GitHub repository.
9.  Short project demonstration.

## 10. Learning Outcomes

By the end of the project, students should be able to explain:

-   The difference between frontend and backend.
-   How a Java application sends an HTTP request to Python.
-   What a REST API and JSON response are.
-   How CRUD operations work.
-   What primary keys and foreign keys represent.
-   How to organize information into related tables.
-   How role-based access works.
-   How a borrowing workflow changes data in multiple sheets.
-   How to test and debug an application.

## 11. Guidance for the Teacher / Project Mentor

Do not ask students to build every feature immediately. Use the
checkpoints to review understanding.

At each checkpoint, ask students to: - Explain what they built. -
Demonstrate it working. - Describe one bug they encountered and how they
fixed it. - Explain where the data is stored. - Identify which part
belongs to the frontend and which belongs to the backend.

The most important first achievement is a working `GET /books` endpoint
that reads real records from Excel. Once students understand that
complete path, they can extend the same pattern to other features.
