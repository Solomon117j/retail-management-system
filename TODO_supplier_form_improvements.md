# TODO: Supplier Form Improvements

## Plan Breakdown and Steps

1. **[x] Add new fields to Supplier model in `procurement/models.py`**
   - Added: website, tax_id, industry, notes

2. **[x] Create `procurement/forms.py` with SupplierForm**
   - ModelForm with all fields, Bootstrap widgets, help texts, and validation

3. **[x] Update `procurement/views.py` to use SupplierForm**
   - Set `form_class = SupplierForm` in SupplierCreateView and SupplierUpdateView
   - Remove old `fields` list

4. **[x] Update `procurement/templates/procurement/supplier_form.html`**
   - Render fields individually with Bootstrap styling and layout
   - Include field labels, errors, and help texts

5. **[In Progress] Run Django migrations**
   - `python manage.py makemigrations procurement`
   - `python manage.py migrate`

6. **[ ] Test the form**
   - Create a new supplier via the form
   - Verify styling, validation, and data saving
   - Update an existing supplier

## Next Steps
- Proceed with step 3: Update views.py
