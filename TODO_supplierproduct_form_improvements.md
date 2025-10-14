# TODO: SupplierProduct Form Improvements

## Plan Breakdown and Steps

1. **[x] Create `SupplierProductForm` in `procurement/forms.py`**
   - ModelForm with all fields, Bootstrap widgets, help texts, and validation

2. **[x] Update `procurement/views.py` to use SupplierProductForm**
   - Set `form_class = SupplierProductForm` in SupplierProductCreateView and SupplierProductUpdateView
   - Remove old `fields` list

3. **[x] Update `procurement/templates/procurement/supplierproduct_form.html`**
   - Render fields individually with Bootstrap styling and layout

4. **[ ] Test the form**
   - Create a new supplier product via the form
   - Verify styling, validation, and data saving
   - Update an existing supplier product

## Next Steps
- Proceed with step 4: Test the form
