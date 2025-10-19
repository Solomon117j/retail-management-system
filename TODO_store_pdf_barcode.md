# TODO: Add PDF Generation with Barcode for Stores

## Tasks
- [ ] Add store_number field to Store model (unique CharField, auto-generated)
- [ ] Add barcode generation method to Store model
- [ ] Update requirements.txt with reportlab and python-barcode
- [ ] Create generate_store_pdf view in store_management/views.py
- [ ] Add URL pattern for PDF generation in store_management/urls.py
- [ ] Update store_detail.html template to include "Generate PDF" button
- [ ] Run database migrations
- [ ] Install new dependencies
- [ ] Test PDF generation functionality
