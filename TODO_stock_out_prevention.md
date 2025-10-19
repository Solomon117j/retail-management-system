# Stock Out Prevention Implementation

## Tasks
- [ ] Add stock checking utility functions in e_commerce/views.py
- [ ] Modify AddToCartView to validate stock before adding items
- [ ] Modify CheckoutView to validate stock before processing orders
- [ ] Add stock decrement logic when orders are confirmed/paid
- [ ] Add stock restoration logic when orders are cancelled
- [ ] Update ProductDetailView to show exact stock quantities
- [ ] Update product_detail.html template to disable out-of-stock actions
- [ ] Update cart.html template to show stock warnings
- [ ] Add stock movement records for all stock changes
- [ ] Test the complete flow to ensure no overselling
