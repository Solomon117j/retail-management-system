# Checkout Form Update Plan

## Objective
Edit checkout forms to include individual required payment fields:
- Card Number (required)
- Expiry Month (required)
- Expiry Year (required)
- CVV (required)
- Card Holder Name (required)

## Current State Analysis
- `payment_form.html`: Uses Stripe Payment Element (single generic element)
- `guest_checkout.html`: Uses Stripe Payment Element (single generic element)
- `GuestCheckoutSerializer`: Already has individual fields defined and required
- Need to replace Stripe Elements with individual form fields

## Plan
1. Update `e_commerce/templates/e_commerce/payment_form.html`
   - Replace Stripe Payment Element with individual input fields
   - Add required attributes and validation
   - Update JavaScript to handle individual fields

2. Update `e_commerce/templates/e_commerce/guest_checkout.html`
   - Replace Stripe Payment Element with individual input fields
   - Add required attributes and validation
   - Update JavaScript to handle individual fields

3. Test both forms to ensure proper validation and submission

## Files to Edit
- `e_commerce/templates/e_commerce/payment_form.html`
- `e_commerce/templates/e_commerce/guest_checkout.html`

## Changes Made
- [x] Updated `payment_form.html` to include individual payment fields
- [x] Updated `guest_checkout.html` to include individual payment fields
- [x] Removed Stripe Elements JavaScript and replaced with basic form validation
- [x] Added required attributes to all payment fields
- [x] Added proper labels and placeholders for user experience

## Followup Steps
- [ ] Test both forms to ensure validation works
- [ ] Verify payment processing still functions with individual fields
- [ ] Check that required field validation prevents submission when empty
- [ ] Test end-to-end payment flow with backend processing
