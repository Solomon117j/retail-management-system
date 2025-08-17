# Retail Management System - Database Schema Documentation

## Table of Contents
1. [Database Overview](#1-database-overview)
2. [Core Tables](#2-core-tables)
3. [Relationship Diagrams](#3-relationship-diagrams)
4. [Table Specifications](#4-table-specifications)
5. [Indexes and Constraints](#5-indexes-and-constraints)
6. [Data Dictionary](#6-data-dictionary)

---

## 1. Database Overview

### Database Configuration
- **Database Engine**: SQLite (Development) / PostgreSQL (Production)
- **Django Version**: 5.2.4
- **ORM**: Django ORM
- **Character Set**: UTF-8
- **Collation**: Default

### Schema Statistics
- **Total Tables**: 15+ (including Django system tables)
- **Custom Tables**: 12
- **Relationships**: 20+ foreign key relationships
- **Indexes**: Auto-generated primary keys + custom indexes

---

## 2. Core Tables

### 2.1 User Management Tables
```sql
-- Custom User Model (Employee)
human_resources_employee
├── employee_id (PK, AutoField)
├── username (CharField, Unique)
├── email (EmailField, Unique)
├── first_name (CharField)
├── last_name (CharField)
├── phone (CharField, Nullable)
├── hire_date (DateField, Nullable)
├── position (CharField)
├── salary (DecimalField, Nullable)
├── department_id (FK to Department)
├── store_id (FK to Store)
├── is_active (BooleanField)
├── is_staff (BooleanField)
├── is_superuser (BooleanField)
├── date_joined (DateTimeField)
└── last_login (DateTimeField, Nullable)
```

### 2.2 Store Management Tables
```sql
-- Store Table
store_management_store
├── id (PK, AutoField) [store_id]
├── store_name (CharField)
├── address (CharField)
├── city (CharField)
├── region (CharField)
├── postal_code (CharField, Nullable)
├── phone (CharField)
├── opening_date (DateField)
├── manager_id (FK to Employee, Nullable)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

-- Department Table
store_management_department
├── id (PK, AutoField)
├── department_name (CharField)
├── description (CharField, Nullable)
├── store_id (FK to Store)
├── manager_id (FK to Employee, Nullable)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

### 2.3 Inventory Management Tables
```sql
-- Category Table
inventory_category
├── id (PK, AutoField)
├── name (CharField)
├── description (CharField, Nullable)
├── parent_id (FK to Category, Nullable)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

-- Brand Table
inventory_brand
├── id (PK, AutoField)
├── name (CharField)
├── description (CharField, Nullable)
├── website (URLField, Nullable)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

-- Product Table
inventory_product
├── id (PK, AutoField)
├── name (CharField)
├── description (CharField, Nullable)
├── category_id (FK to Category)
├── brand_id (FK to Brand, Nullable)
├── unit_price (DecimalField)
├── cost_price (DecimalField, Nullable)
├── stock_quantity (IntegerField)
├── reorder_level (IntegerField)
├── barcode (CharField, Unique, Nullable)
├── is_active (BooleanField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

### 2.4 Sales Management Tables
```sql
-- Sale Table
sales_sale
├── id (PK, AutoField)
├── sale_date (DateTimeField)
├── employee_id (FK to Employee)
├── customer_name (CharField, Nullable)
├── total_amount (DecimalField)
├── payment_method (CharField)
├── status (CharField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

-- Sale Item Table
sales_saleitem
├── id (PK, AutoField)
├── sale_id (FK to Sale)
├── product_id (FK to Product)
├── quantity (IntegerField)
├── unit_price (DecimalField)
├── total_price (DecimalField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

### 2.5 HR Management Tables
```sql
-- Attendance Table
human_resources_attendance
├── id (PK, AutoField)
├── employee_id (FK to Employee)
├── date (DateField)
├── time_in (TimeField, Nullable)
├── time_out (TimeField, Nullable)
├── break_duration (DurationField, Nullable)
├── total_hours (DecimalField, Nullable)
├── status (CharField)
├── notes (TextField, Nullable)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

-- Payroll Table
human_resources_payroll
├── id (PK, AutoField)
├── employee_id (FK to Employee)
├── pay_period_start (DateField)
├── pay_period_end (DateField)
├── basic_salary (DecimalField)
├── overtime_hours (DecimalField)
├── overtime_rate (DecimalField)
├── gross_pay (DecimalField)
├── tax_deduction (DecimalField)
├── other_deductions (DecimalField)
├── net_pay (DecimalField)
├── status (CharField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

### 2.6 Procurement Tables
```sql
-- Supplier Table
procurement_supplier
├── id (PK, AutoField)
├── name (CharField)
├── contact_person (CharField, Nullable)
├── email (EmailField, Nullable)
├── phone (CharField, Nullable)
├── address (TextField, Nullable)
├── city (CharField, Nullable)
├── country (CharField, Nullable)
├── is_active (BooleanField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)

-- Purchase Order Table
procurement_purchaseorder
├── id (PK, AutoField)
├── order_number (CharField, Unique)
├── supplier_id (FK to Supplier)
├── order_date (DateField)
├── expected_delivery (DateField, Nullable)
├── total_amount (DecimalField)
├── status (CharField)
├── notes (TextField, Nullable)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

---

## 3. Relationship Diagrams

### 3.1 Core Entity Relationships
```
Employee (1) ──────────── (M) Attendance
    │                         │
    │                         │
    ├── (1) ──────────── (M) Payroll
    │                         │
    │                         │
    ├── (M) ──────────── (1) Department
    │                         │
    │                         │
    ├── (M) ──────────── (1) Store
    │                         │
    │                         │
    └── (1) ──────────── (M) Sale
                              │
                              │
                         (1) ──┴── (M) SaleItem
                                        │
                                        │
                                   (M) ──┴── (1) Product
                                                │
                                                │
                                           (M) ──┼── (1) Category
                                                │
                                                │
                                           (M) ──┴── (1) Brand
```

### 3.2 Store Management Relationships
```
Store (1) ──────────── (M) Department
  │                         │
  │                         │
  ├── (1) ──────────── (M) Employee (as store assignment)
  │                         │
  │                         │
  └── (1) ──────────── (1) Employee (as manager)
                            │
                            │
Department (1) ──────────── (M) Employee (as department assignment)
     │                      │
     │                      │
     └── (1) ──────────── (1) Employee (as manager)
```

### 3.3 Inventory Relationships
```
Category (1) ──────────── (M) Product
    │                         │
    │                         │
    └── (1) ──────────── (M) Category (self-referencing)

Brand (1) ──────────── (M) Product

Product (1) ──────────── (M) SaleItem
    │                         │
    │                         │
    └── (1) ──────────── (M) PurchaseOrderItem
```

---

## 4. Table Specifications

### 4.1 Employee Table (Custom User Model)
```sql
CREATE TABLE human_resources_employee (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    hire_date DATE,
    position VARCHAR(50),
    salary DECIMAL(10,2),
    department_id INTEGER REFERENCES store_management_department(id),
    store_id INTEGER REFERENCES store_management_store(id),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    password VARCHAR(128) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Store Table
```sql
CREATE TABLE store_management_store (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_name VARCHAR(100) NOT NULL,
    address VARCHAR(200) NOT NULL,
    city VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    postal_code VARCHAR(20),
    phone VARCHAR(20) NOT NULL,
    opening_date DATE NOT NULL,
    manager_id INTEGER REFERENCES human_resources_employee(employee_id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.3 Product Table
```sql
CREATE TABLE inventory_product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    category_id INTEGER NOT NULL REFERENCES inventory_category(id),
    brand_id INTEGER REFERENCES inventory_brand(id),
    unit_price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2),
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    reorder_level INTEGER NOT NULL DEFAULT 10,
    barcode VARCHAR(50) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT positive_price CHECK (unit_price > 0),
    CONSTRAINT non_negative_stock CHECK (stock_quantity >= 0),
    CONSTRAINT positive_reorder CHECK (reorder_level > 0)
);
```

### 4.4 Sale Table
```sql
CREATE TABLE sales_sale (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    employee_id INTEGER NOT NULL REFERENCES human_resources_employee(employee_id),
    customer_name VARCHAR(100),
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'completed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT positive_total CHECK (total_amount > 0),
    CONSTRAINT valid_payment_method CHECK (payment_method IN ('cash', 'card', 'mobile', 'credit')),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'completed', 'cancelled', 'refunded'))
);
```

### 4.5 Attendance Table
```sql
CREATE TABLE human_resources_attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL REFERENCES human_resources_employee(employee_id),
    date DATE NOT NULL,
    time_in TIME,
    time_out TIME,
    break_duration INTEGER, -- in minutes
    total_hours DECIMAL(4,2),
    status VARCHAR(20) DEFAULT 'present',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_status CHECK (status IN ('present', 'absent', 'late', 'half_day', 'overtime')),
    CONSTRAINT unique_employee_date UNIQUE (employee_id, date),
    CONSTRAINT valid_hours CHECK (total_hours >= 0 AND total_hours <= 24)
);
```

---

## 5. Indexes and Constraints

### 5.1 Primary Key Indexes
```sql
-- Automatically created for all primary keys
CREATE INDEX idx_employee_pk ON human_resources_employee(employee_id);
CREATE INDEX idx_store_pk ON store_management_store(id);
CREATE INDEX idx_product_pk ON inventory_product(id);
-- ... etc for all tables
```

### 5.2 Foreign Key Indexes
```sql
-- Employee relationships
CREATE INDEX idx_employee_department ON human_resources_employee(department_id);
CREATE INDEX idx_employee_store ON human_resources_employee(store_id);

-- Store relationships
CREATE INDEX idx_store_manager ON store_management_store(manager_id);
CREATE INDEX idx_department_store ON store_management_department(store_id);
CREATE INDEX idx_department_manager ON store_management_department(manager_id);

-- Product relationships
CREATE INDEX idx_product_category ON inventory_product(category_id);
CREATE INDEX idx_product_brand ON inventory_product(brand_id);

-- Sales relationships
CREATE INDEX idx_sale_employee ON sales_sale(employee_id);
CREATE INDEX idx_saleitem_sale ON sales_saleitem(sale_id);
CREATE INDEX idx_saleitem_product ON sales_saleitem(product_id);

-- HR relationships
CREATE INDEX idx_attendance_employee ON human_resources_attendance(employee_id);
CREATE INDEX idx_payroll_employee ON human_resources_payroll(employee_id);
```

### 5.3 Unique Constraints
```sql
-- Employee constraints
ALTER TABLE human_resources_employee ADD CONSTRAINT uk_employee_username UNIQUE (username);
ALTER TABLE human_resources_employee ADD CONSTRAINT uk_employee_email UNIQUE (email);

-- Product constraints
ALTER TABLE inventory_product ADD CONSTRAINT uk_product_barcode UNIQUE (barcode);

-- Attendance constraints
ALTER TABLE human_resources_attendance ADD CONSTRAINT uk_attendance_employee_date UNIQUE (employee_id, date);

-- Purchase order constraints
ALTER TABLE procurement_purchaseorder ADD CONSTRAINT uk_po_number UNIQUE (order_number);
```

### 5.4 Check Constraints
```sql
-- Employee constraints
ALTER TABLE human_resources_employee ADD CONSTRAINT chk_employee_salary CHECK (salary IS NULL OR salary > 0);

-- Product constraints
ALTER TABLE inventory_product ADD CONSTRAINT chk_product_price CHECK (unit_price > 0);
ALTER TABLE inventory_product ADD CONSTRAINT chk_product_stock CHECK (stock_quantity >= 0);
ALTER TABLE inventory_product ADD CONSTRAINT chk_product_reorder CHECK (reorder_level > 0);

-- Sales constraints
ALTER TABLE sales_sale ADD CONSTRAINT chk_sale_total CHECK (total_amount > 0);
ALTER TABLE sales_saleitem ADD CONSTRAINT chk_saleitem_quantity CHECK (quantity > 0);
ALTER TABLE sales_saleitem ADD CONSTRAINT chk_saleitem_price CHECK (unit_price > 0);

-- Attendance constraints
ALTER TABLE human_resources_attendance ADD CONSTRAINT chk_attendance_hours CHECK (total_hours >= 0 AND total_hours <= 24);

-- Payroll constraints
ALTER TABLE human_resources_payroll ADD CONSTRAINT chk_payroll_basic CHECK (basic_salary > 0);
ALTER TABLE human_resources_payroll ADD CONSTRAINT chk_payroll_overtime_hours CHECK (overtime_hours >= 0);
ALTER TABLE human_resources_payroll ADD CONSTRAINT chk_payroll_gross CHECK (gross_pay > 0);
```

---

## 6. Data Dictionary

### 6.1 Employee Fields
| Field | Type | Length | Null | Default | Description |
|-------|------|--------|------|---------|-------------|
| employee_id | AutoField | - | No | Auto | Primary key, unique employee identifier |
| username | CharField | 150 | No | - | Unique username for login |
| email | EmailField | 254 | No | - | Unique email address |
| first_name | CharField | 50 | No | - | Employee's first name |
| last_name | CharField | 50 | No | - | Employee's last name |
| phone | CharField | 20 | Yes | NULL | Contact phone number |
| hire_date | DateField | - | Yes | NULL | Date employee was hired |
| position | CharField | 50 | Yes | '' | Job position/title |
| salary | DecimalField | 10,2 | Yes | NULL | Monthly salary amount |
| department_id | ForeignKey | - | Yes | NULL | Reference to department |
| store_id | ForeignKey | - | Yes | NULL | Reference to assigned store |
| is_active | BooleanField | - | No | True | Whether employee is active |
| is_staff | BooleanField | - | No | False | Django admin access |
| is_superuser | BooleanField | - | No | False | Django superuser status |
| date_joined | DateTimeField | - | No | Now | Account creation date |
| last_login | DateTimeField | - | Yes | NULL | Last login timestamp |

### 6.2 Product Fields
| Field | Type | Length | Null | Default | Description |
|-------|------|--------|------|---------|-------------|
| id | AutoField | - | No | Auto | Primary key |
| name | CharField | 100 | No | - | Product name |
| description | CharField | 500 | Yes | NULL | Product description |
| category_id | ForeignKey | - | No | - | Product category |
| brand_id | ForeignKey | - | Yes | NULL | Product brand |
| unit_price | DecimalField | 10,2 | No | - | Selling price per unit |
| cost_price | DecimalField | 10,2 | Yes | NULL | Cost price per unit |
| stock_quantity | IntegerField | - | No | 0 | Current stock level |
| reorder_level | IntegerField | - | No | 10 | Minimum stock threshold |
| barcode | CharField | 50 | Yes | NULL | Product barcode (unique) |
| is_active | BooleanField | - | No | True | Whether product is active |

### 6.3 Sale Fields
| Field | Type | Length | Null | Default | Description |
|-------|------|--------|------|---------|-------------|
| id | AutoField | - | No | Auto | Primary key |
| sale_date | DateTimeField | - | No | Now | Date and time of sale |
| employee_id | ForeignKey | - | No | - | Employee who made the sale |
| customer_name | CharField | 100 | Yes | NULL | Customer name (optional) |
| total_amount | DecimalField | 10,2 | No | - | Total sale amount |
| payment_method | CharField | 20 | No | - | Payment method used |
| status | CharField | 20 | No | 'completed' | Sale status |

### 6.4 Attendance Fields
| Field | Type | Length | Null | Default | Description |
|-------|------|--------|------|---------|-------------|
| id | AutoField | - | No | Auto | Primary key |
| employee_id | ForeignKey | - | No | - | Employee reference |
| date | DateField | - | No | - | Attendance date |
| time_in | TimeField | - | Yes | NULL | Clock in time |
| time_out | TimeField | - | Yes | NULL | Clock out time |
| break_duration | IntegerField | - | Yes | NULL | Break time in minutes |
| total_hours | DecimalField | 4,2 | Yes | NULL | Total work hours |
| status | CharField | 20 | No | 'present' | Attendance status |
| notes | TextField | - | Yes | NULL | Additional notes |

### 6.5 Enumerated Values

#### Payment Methods
- `cash` - Cash payment
- `card` - Credit/Debit card
- `mobile` - Mobile payment
- `credit` - Store credit

#### Sale Status
- `pending` - Sale in progress
- `completed` - Sale completed
- `cancelled` - Sale cancelled
- `refunded` - Sale refunded

#### Attendance Status
- `present` - Employee present
- `absent` - Employee absent
- `late` - Employee late
- `half_day` - Half day attendance
- `overtime` - Overtime work

#### Payroll Status
- `draft` - Payroll in preparation
- `approved` - Payroll approved
- `processed` - Payroll processed
- `paid` - Payroll paid

---

## Database Maintenance

### 6.6 Backup Strategy
```sql
-- Daily backup command
.backup main backup_YYYY_MM_DD.db

-- Restore command
.restore main backup_YYYY_MM_DD.db
```

### 6.7 Performance Optimization
```sql
-- Analyze database statistics
ANALYZE;

-- Vacuum database (SQLite)
VACUUM;

-- Reindex all indexes
REINDEX;
```

### 6.8 Data Integrity Checks
```sql
-- Check foreign key constraints
PRAGMA foreign_key_check;

-- Check database integrity
PRAGMA integrity_check;

-- Check quick integrity
PRAGMA quick_check;
```

---

*Document Version: 1.0*  
*Last Updated: December 2024*  
*Prepared by: Database Team*