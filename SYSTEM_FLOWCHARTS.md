# Retail Management System - Flow Charts & Process Diagrams

## Table of Contents
1. [System Architecture Flow](#1-system-architecture-flow)
2. [User Authentication Flow](#2-user-authentication-flow)
3. [Employee Management Flow](#3-employee-management-flow)
4. [Inventory Management Flow](#4-inventory-management-flow)
5. [Sales Process Flow](#5-sales-process-flow)
6. [Payroll Processing Flow](#6-payroll-processing-flow)
7. [Data Flow Diagrams](#7-data-flow-diagrams)

---

## 1. System Architecture Flow

### High-Level System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                     │
├─────────────────────────────────────────────────────────────┤
│  Web Browser │ Mobile App │ API Clients │ Admin Interface  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   WEB SERVER LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  Nginx/Apache │ Load Balancer │ SSL Termination │ Caching  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 APPLICATION SERVER LAYER                    │
├─────────────────────────────────────────────────────────────┤
│  Django Application │ Gunicorn │ WSGI │ Session Management │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                      │
├─────────────────────────────────────────────────────────────┤
│ HR Module │ Store Mgmt │ Inventory │ Sales │ Procurement    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  Django ORM │ Database Connections │ Query Optimization     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATABASE LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL │ SQLite │ Redis Cache │ File Storage          │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. User Authentication Flow

### Login Process Flow
```mermaid
graph TD
    A[User Accesses System] --> B{Already Logged In?}
    B -->|Yes| C[Redirect to Dashboard]
    B -->|No| D[Show Login Page]
    
    D --> E[User Enters Credentials]
    E --> F[Submit Login Form]
    F --> G{CSRF Token Valid?}
    G -->|No| H[Show CSRF Error]
    H --> D
    
    G -->|Yes| I[Validate Credentials]
    I --> J{Credentials Valid?}
    J -->|No| K[Show Error Message]
    K --> L{Max Attempts Reached?}
    L -->|Yes| M[Lock Account]
    L -->|No| D
    
    J -->|Yes| N[Create User Session]
    N --> O[Set Session Cookie]
    O --> P[Log Login Event]
    P --> Q[Check User Permissions]
    Q --> R[Redirect to Dashboard]
    
    M --> S[Send Account Lock Email]
    S --> T[Show Account Locked Message]
```

### Permission Check Flow
```mermaid
graph TD
    A[User Requests Resource] --> B[Check Authentication]
    B --> C{User Authenticated?}
    C -->|No| D[Redirect to Login]
    
    C -->|Yes| E[Get User Permissions]
    E --> F[Check Required Permission]
    F --> G{Permission Granted?}
    G -->|No| H[Show 403 Forbidden]
    G -->|Yes| I[Allow Access]
    
    I --> J[Log Access Event]
    J --> K[Render Requested Page]
```

---

## 3. Employee Management Flow

### Employee Creation Process
```mermaid
graph TD
    A[HR Manager Clicks Add Employee] --> B[Load Employee Form]
    B --> C[Fill Employee Details]
    C --> D[Select Department/Store]
    D --> E[Set Permissions/Role]
    E --> F[Upload Photo (Optional)]
    F --> G[Submit Form]
    
    G --> H{Form Validation}
    H -->|Invalid| I[Show Validation Errors]
    I --> C
    
    H -->|Valid| J{Email Already Exists?}
    J -->|Yes| K[Show Email Error]
    K --> C
    
    J -->|No| L{Username Available?}
    L -->|No| M[Show Username Error]
    M --> C
    
    L -->|Yes| N[Create Employee Record]
    N --> O[Generate Employee ID]
    O --> P[Hash Password]
    P --> Q[Save to Database]
    Q --> R[Create User Account]
    R --> S[Send Welcome Email]
    S --> T[Log Creation Event]
    T --> U[Redirect to Employee List]
```

### Employee Update Process
```mermaid
graph TD
    A[Select Employee to Edit] --> B[Load Current Data]
    B --> C[Display Edit Form]
    C --> D[Modify Employee Details]
    D --> E[Submit Changes]
    
    E --> F{Form Validation}
    F -->|Invalid| G[Show Validation Errors]
    G --> D
    
    F -->|Valid| H{Email Conflict?}
    H -->|Yes| I[Show Email Conflict Error]
    I --> D
    
    H -->|No| J[Update Database Record]
    J --> K[Update Related Records]
    K --> L[Log Update Event]
    L --> M[Send Notification Email]
    M --> N[Show Success Message]
    N --> O[Redirect to Employee Detail]
```

### Employee Deletion Process
```mermaid
graph TD
    A[Click Delete Employee] --> B[Show Delete Confirmation]
    B --> C[Display Employee Details]
    C --> D[Show Consequences Warning]
    D --> E{User Confirms?}
    E -->|No| F[Cancel Operation]
    F --> G[Return to Employee List]
    
    E -->|Yes| H[Check Dependencies]
    H --> I{Has Active Records?}
    I -->|Yes| J[Show Dependency Warning]
    J --> K{Force Delete?}
    K -->|No| F
    
    I -->|No| L[Soft Delete Employee]
    K -->|Yes| L
    L --> M[Update Related Records]
    M --> N[Archive Employee Data]
    N --> O[Log Deletion Event]
    O --> P[Send Notification]
    P --> Q[Show Success Message]
    Q --> G
```

---

## 4. Inventory Management Flow

### Product Addition Flow
```mermaid
graph TD
    A[Inventory Manager Access] --> B[Click Add Product]
    B --> C[Load Product Form]
    C --> D[Enter Product Details]
    D --> E[Select Category]
    E --> F[Select/Create Brand]
    F --> G[Set Pricing Information]
    G --> H[Set Stock Levels]
    H --> I[Upload Product Images]
    I --> J[Set Reorder Levels]
    J --> K[Submit Form]
    
    K --> L{Form Validation}
    L -->|Invalid| M[Show Validation Errors]
    M --> D
    
    L -->|Valid| N{SKU Already Exists?}
    N -->|Yes| O[Show SKU Conflict Error]
    O --> D
    
    N -->|No| P[Generate Product ID]
    P --> Q[Save Product to Database]
    Q --> R[Create Initial Stock Record]
    R --> S[Generate Barcode]
    S --> T[Log Product Creation]
    T --> U[Show Success Message]
    U --> V[Redirect to Product List]
```

### Stock Update Flow
```mermaid
graph TD
    A[Select Product for Stock Update] --> B[Display Current Stock]
    B --> C[Choose Update Type]
    C --> D{Update Type?}
    
    D -->|Stock In| E[Enter Received Quantity]
    D -->|Stock Out| F[Enter Sold/Used Quantity]
    D -->|Adjustment| G[Enter Adjustment Quantity]
    
    E --> H[Enter Supplier Info]
    F --> I[Enter Sale/Usage Reason]
    G --> J[Enter Adjustment Reason]
    
    H --> K[Calculate New Stock Level]
    I --> K
    J --> K
    
    K --> L{Stock Level Valid?}
    L -->|No| M[Show Stock Error]
    M --> C
    
    L -->|Yes| N[Update Product Stock]
    N --> O[Create Stock Movement Record]
    O --> P[Check Reorder Level]
    P --> Q{Below Reorder Level?}
    Q -->|Yes| R[Generate Low Stock Alert]
    Q -->|No| S[Log Stock Update]
    
    R --> S
    S --> T[Show Success Message]
    T --> U[Update Product Display]
```

### Low Stock Alert Flow
```mermaid
graph TD
    A[System Scheduled Check] --> B[Get All Active Products]
    B --> C[For Each Product]
    C --> D[Check Current Stock]
    D --> E{Stock < Reorder Level?}
    E -->|No| F[Continue to Next Product]
    E -->|Yes| G[Add to Alert List]
    
    F --> H{More Products?}
    G --> H
    H -->|Yes| C
    H -->|No| I{Any Alerts Generated?}
    
    I -->|No| J[End Process]
    I -->|Yes| K[Create Alert Notification]
    K --> L[Send Email to Managers]
    L --> M[Update Dashboard Alerts]
    M --> N[Log Alert Generation]
    N --> J
```

---

## 5. Sales Process Flow

### Point of Sale Flow
```mermaid
graph TD
    A[Sales Person Login] --> B[Open POS Interface]
    B --> C[Start New Sale]
    C --> D[Enter Customer Info (Optional)]
    D --> E[Scan/Search Product]
    E --> F{Product Found?}
    F -->|No| G[Show Product Not Found]
    G --> E
    
    F -->|Yes| H[Check Stock Availability]
    H --> I{Stock Available?}
    I -->|No| J[Show Out of Stock]
    J --> E
    
    I -->|Yes| K[Add Product to Cart]
    K --> L[Enter Quantity]
    L --> M[Calculate Line Total]
    M --> N[Update Cart Display]
    N --> O{Add More Products?}
    O -->|Yes| E
    
    O -->|No| P[Calculate Sale Total]
    P --> Q[Apply Discounts (If Any)]
    Q --> R[Calculate Tax]
    R --> S[Display Final Total]
    S --> T[Select Payment Method]
    T --> U{Payment Method?}
    
    U -->|Cash| V[Enter Amount Received]
    U -->|Card| W[Process Card Payment]
    U -->|Mobile| X[Process Mobile Payment]
    
    V --> Y[Calculate Change]
    W --> Z[Verify Payment]
    X --> Z
    Y --> AA[Process Sale]
    Z --> AA
    
    AA --> BB[Update Inventory]
    BB --> CC[Generate Receipt]
    CC --> DD[Print Receipt]
    DD --> EE[Save Sale Record]
    EE --> FF[Show Success Message]
    FF --> GG[Clear Cart for Next Sale]
```

### Sales Reporting Flow
```mermaid
graph TD
    A[Manager Access Reports] --> B[Select Report Type]
    B --> C{Report Type?}
    
    C -->|Daily Sales| D[Get Today's Sales]
    C -->|Employee Performance| E[Get Employee Sales Data]
    C -->|Product Analysis| F[Get Product Sales Data]
    C -->|Custom Report| G[Set Custom Parameters]
    
    D --> H[Calculate Daily Totals]
    E --> I[Calculate Employee Metrics]
    F --> J[Calculate Product Metrics]
    G --> K[Apply Custom Filters]
    
    H --> L[Generate Report Data]
    I --> L
    J --> L
    K --> L
    
    L --> M[Format Report]
    M --> N[Display Report]
    N --> O{Export Required?}
    O -->|No| P[End Process]
    O -->|Yes| Q[Select Export Format]
    Q --> R{Export Format?}
    
    R -->|PDF| S[Generate PDF]
    R -->|Excel| T[Generate Excel]
    R -->|CSV| U[Generate CSV]
    
    S --> V[Download File]
    T --> V
    U --> V
    V --> P
```

---

## 6. Payroll Processing Flow

### Monthly Payroll Process
```mermaid
graph TD
    A[HR Manager Initiates Payroll] --> B[Select Pay Period]
    B --> C[Get Active Employees]
    C --> D[For Each Employee]
    D --> E[Get Basic Salary]
    E --> F[Get Attendance Data]
    F --> G[Calculate Regular Hours]
    G --> H[Calculate Overtime Hours]
    H --> I[Calculate Overtime Pay]
    I --> J[Calculate Gross Pay]
    J --> K[Calculate Tax Deductions]
    K --> L[Calculate Other Deductions]
    L --> M[Calculate Net Pay]
    M --> N[Create Payroll Record]
    N --> O{More Employees?}
    O -->|Yes| D
    
    O -->|No| P[Generate Payroll Summary]
    P --> Q[Review Payroll Data]
    Q --> R{Approve Payroll?}
    R -->|No| S[Make Adjustments]
    S --> Q
    
    R -->|Yes| T[Process Payments]
    T --> U[Generate Pay Slips]
    U --> V[Send Pay Slips to Employees]
    V --> W[Update Accounting Records]
    W --> X[Archive Payroll Data]
    X --> Y[Generate Payroll Reports]
    Y --> Z[End Process]
```

### Attendance Calculation Flow
```mermaid
graph TD
    A[Get Employee Attendance] --> B[Get Pay Period Dates]
    B --> C[For Each Work Day]
    C --> D[Check Attendance Record]
    D --> E{Attended?}
    E -->|No| F[Mark as Absent]
    E -->|Yes| G[Get Clock In/Out Times]
    
    F --> H[Deduct from Pay]
    G --> I[Calculate Work Hours]
    I --> J[Subtract Break Time]
    J --> K[Calculate Regular Hours]
    K --> L{Hours > Standard?}
    L -->|No| M[Add to Regular Hours Total]
    L -->|Yes| N[Split Regular/Overtime]
    N --> O[Add to Overtime Hours]
    
    H --> P{More Days?}
    M --> P
    O --> P
    P -->|Yes| C
    P -->|No| Q[Calculate Total Hours]
    Q --> R[Return Attendance Summary]
```

---

## 7. Data Flow Diagrams

### Level 0 - Context Diagram
```
                    ┌─────────────────┐
                    │   HR Manager    │
                    └─────────────────┘
                            │
                            ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │ Store Manager   │───▶│     RETAIL      │◀───│ Sales Person    │
    └─────────────────┘    │   MANAGEMENT    │    └─────────────────┘
                           │     SYSTEM      │
    ┌─────────────────┐    │                 │    ┌─────────────────┐
    │Inventory Manager│───▶│                 │◀───│   Customer      │
    └─────────────────┘    └─────────────────┘    └─────────────────┘
                            │
                            ▼
                    ┌─────────────────┐
                    │   Admin User    │
                    └─────────────────┘
```

### Level 1 - System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Login    │───▶│  Authentication │───▶│   Dashboard     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Employee Mgmt   │    │   Store Mgmt    │    │ Inventory Mgmt  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Sales Process  │    │ Payroll Process │    │   Reporting     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                           │
└─────────────────────────────────────────────────────────────┘
```

### Data Store Relationships
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Employees     │───▶│   Attendance    │───▶│    Payroll      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                             │
         ▼                                             ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Sales       │───▶│   Sale Items    │───▶│    Products     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Stores      │    │   Departments   │    │   Categories    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## Process Flow Summary

### Key System Processes
1. **Authentication**: Secure user login and session management
2. **Employee Management**: Complete employee lifecycle management
3. **Inventory Control**: Real-time stock management and alerts
4. **Sales Processing**: Point-of-sale and transaction management
5. **Payroll Processing**: Automated payroll calculation and distribution
6. **Reporting**: Comprehensive business intelligence and analytics

### Integration Points
- **HR ↔ Payroll**: Employee data feeds payroll calculations
- **Sales ↔ Inventory**: Sales transactions update stock levels
- **Employees ↔ Sales**: Employee assignments track sales performance
- **Stores ↔ Inventory**: Store-specific inventory management
- **All Modules ↔ Reporting**: Data aggregation for business intelligence

### Security Checkpoints
- User authentication at system entry
- Permission validation for each module access
- CSRF protection for all form submissions
- Audit logging for critical operations
- Data validation at multiple layers

---

*Document Version: 1.0*  
*Last Updated: December 2024*  
*Prepared by: System Development Team*