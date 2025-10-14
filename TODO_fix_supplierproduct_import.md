# TODO: Fix SupplierProduct Import in procurement/forms.py

## Steps to Complete:
- [x] Update the import statement in `procurement/forms.py` to include `SupplierProduct` from `.models`
- [x] Verify the file syntax and ensure no other import issues

## Information Gathered:
- `procurement/forms.py` imports `Supplier`, `PurchaseOrder`, and `PurchaseOrderItem` from `.models`, but not `SupplierProduct`.
- `procurement/models.py` defines the `SupplierProduct` model correctly.
- The `SupplierProductForm` in `forms.py` uses `model = SupplierProduct`, causing the NameError.

## Plan:
- Update the import statement in `procurement/forms.py` to include `SupplierProduct`.

## Dependent Files:
- `procurement/forms.py`

## Followup Steps:
- After editing, verify the file syntax and test the application to ensure the form works without errors.
