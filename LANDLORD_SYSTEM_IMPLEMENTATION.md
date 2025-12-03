# Landlord Management System Implementation Guide

## Overview

This guide provides a step-by-step implementation to transform the existing retail management system into a comprehensive landlord management system with tenant functionality. The current Django-based system will be adapted to manage properties, units, tenants, leases, and rent payments.

## Current System Analysis

### Existing Modules
- **accounts**: User authentication and authorization
- **dashboards**: Main dashboard and landing pages
- **store_management**: Multi-store support (will become property management)
- **human_resources**: Employee lifecycle management (will become tenant management)
- **inventory**: Product and stock management (may be repurposed for property assets)
- **e_commerce**: Online sales platform (may be repurposed for online property listings)
- **sales**: Sales transactions (will become rent payment processing)
- **reporting**: Analytics and reporting
- **api**: RESTful API endpoints

### Key Models to Adapt
- `Store` → `Property`
- `Department` → `PropertyUnit`
- `Employee` → `Tenant`
- `Attendance` → `LeaseAgreement`
- `Payroll` → `RentPayment`

## Implementation Steps

### Step 1: Database Backup and Preparation

1. **Create a full database backup**
   ```bash
   python manage.py dumpdata > pre_landlord_migration.json
   ```

2. **Create a new migration branch**
   ```bash
   git checkout -b landlord-system-migration
   ```

### Step 2: Rename and Adapt Core Models

#### 2.1 Update store_management/models.py

**Rename Store to Property:**
```python
class Property(models.Model):  # Renamed from Store
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property_number = models.CharField(  # Renamed from store_number
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Property Number",
        help_text="Unique property identifier, auto-generated if left blank"
    )
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=50)
    region = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20)
    acquisition_date = models.DateField()  # Renamed from opening_date
    property_manager = models.ForeignKey(  # Renamed from manager
        'human_resources.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_properties',
        verbose_name="Property Manager"
    )

    # Property characteristics
    property_type = models.CharField(  # Renamed from store_type
        max_length=20,
