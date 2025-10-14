# Customer Registration Improvements - TODO

## Overview
Enhance the customer registration form to collect more comprehensive data for better customer profiling and personalized services.

## Tasks

### 1. Update Customer Model (sales/models.py)
- [ ] Add middle_name field
- [ ] Add country and state fields
- [ ] Add occupation field
- [ ] Add marital_status field
- [ ] Add number_of_dependents field
- [ ] Add referral_source field
- [ ] Add emergency_contact_name and emergency_contact_phone fields
- [ ] Add language_preference field
- [ ] Add data_processing_consent field
- [ ] Add notification preferences (email_notifications, sms_notifications, push_notifications)

### 2. Update CustomerForm (sales/forms.py)
- [ ] Add new fields to Meta.fields
- [ ] Add appropriate widgets with Bootstrap classes
- [ ] Add validation for phone numbers and required consents
- [ ] Add choice fields for marital_status, referral_source, language_preference

### 3. Update Template (sales/templates/sales/customer_form.html)
- [ ] Reorganize form into logical sections with Bootstrap cards/accordions
- [ ] Add Personal Information section (name, DOB, gender, marital status, dependents)
- [ ] Add Contact Information section (address, country, state, emergency contact)
- [ ] Add Preferences section (language, notifications, marketing)
- [ ] Add Business Information section (occupation, referral source, membership)
- [ ] Add help text and placeholders for better UX

### 4. Create and Run Migration
- [ ] Generate migration for new model fields
- [ ] Run migration to update database schema

### 5. Testing and Validation
- [ ] Test form submission with all new fields
- [ ] Verify validation works correctly
- [ ] Check template renders properly
- [ ] Test responsive design on different screen sizes

### 6. Additional Enhancements (Future)
- [ ] Add JavaScript for dynamic country/state dropdowns
- [ ] Implement conditional field display based on selections
- [ ] Add form progress indicator
- [ ] Consider multi-step form wizard for better UX
