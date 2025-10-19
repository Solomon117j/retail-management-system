# Stock Out Prevention Implementation - Active Tasks

## Current Status
- [x] Analysis complete - partial stock checking exists but needs completion
- [ ] Implementation in progress

## Tasks to Complete
- [ ] Enhance stock checking utilities in e_commerce/views.py
- [ ] Add stock validation to CheckoutView before order creation
- [ ] Add stock validation to GuestCheckoutView before order creation
- [ ] Modify payment success handling to decrement stock immediately
- [ ] Ensure stock restoration works for both authenticated and guest orders
- [ ] Update ProductDetailView to show exact stock quantities
- [ ] Update product_detail.html template for stock warnings and disabled actions
- [ ] Update cart.html template for stock warnings
- [ ] Update guest_checkout.html template for stock warnings
- [ ] Test complete flow: add to cart → checkout → payment → stock decrement
- [ ] Test cancellation flow: stock restoration
- [ ] Test guest checkout stock validation
- [ ] Update TODO_stock_out_prevention.md with completion status

## Implementation Notes
- Stock checking exists in OptionalLoginMixin.get_available_stock()
- Stock management exists in OnlineOrderStatusUpdateView._decrease_stock_for_order()
- Need to add stock validation to checkout flows before order creation
- Payment success should trigger stock decrement, not just status changes
- Ensure both authenticated and guest checkout validate stock
