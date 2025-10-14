+# Inventory Module Comprehensive Data Collection Improvements

## Tasks
- [x] Update inventory/templates/inventory/product_form.html to include missing fields: barcode, weight, length, width, height, image, default_supplier
- [x] Update inventory/templates/inventory/inventoryrecord_form.html to include missing fields: batch_number, expiration_date, cost_price, supplier
- [x] Update inventory/templates/inventory/stockmovement_form.html to include missing field: reference
- [x] Enhance inventory/templates/inventory/product_list.html to display more comprehensive data (barcode, dimensions, supplier, reorder_level)
- [x] Enhance inventory/templates/inventory/inventoryrecord_list.html to show batch, expiration, cost_price, supplier, timestamps
- [x] Enhance inventory/templates/inventory/stockmovement_list.html to show reference field
- [ ] Test the updated forms for new data entry
- [ ] Update export functions in views.py to include new fields if needed
- [ ] Verify dashboard views display comprehensive data
