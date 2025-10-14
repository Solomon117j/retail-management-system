# Sales Module Improvements - Comprehensive Data Collection

## Overview
Enhance the sales module forms and listings to collect more comprehensive data for better customer profiling, sales tracking, and analytics.

## Tasks

### 1. Model Enhancements
- [ ] Add additional fields to Customer model (date_of_birth, gender, social_media, preferred_contact, marketing_opt_in, notes)
- [ ] Add additional fields to Sale model (sales_channel, order_status, notes, delivery_address, invoice_number)
- [ ] Add additional fields to SaleItem model if needed (e.g., serial_number, warranty_info)

### 2. Database Migrations
- [ ] Create and apply migrations for model changes

### 3. Form Updates
- [ ] Update CustomerForm in sales/forms.py to include new fields with validation
- [ ] Update SaleForm in sales/forms.py to include new fields with validation
- [ ] Update SaleItemForm if needed

### 4. Template Updates
- [ ] Update customer_form.html to include new fields with proper styling
- [ ] Update customer_list.html to display new data columns
- [ ] Update sale_form.html to include new fields with proper styling
- [ ] Update sale_list.html to display new data columns

### 5. View Updates
- [ ] Update views.py to handle new fields and validation if needed
- [ ] Ensure proper context data for new fields in listings

### 6. Testing and Validation
- [ ] Test customer form creation and editing
- [ ] Test sale form creation and editing
- [ ] Test listing views display new data correctly
- [ ] Validate form submissions and data integrity

## Completion Criteria
- All new fields are properly added to models and forms
- Templates render new fields correctly
- Listings display comprehensive data
- No breaking changes to existing functionality
- Data validation works for new fields
