# TODO: Implement Guest Checkout Functionality

## Tasks
- [x] Modify AddToCartView to support guest users using session-based cart
- [x] Modify CartView to display session cart for guests
- [x] Update cart models or views to handle session carts
- [x] Ensure checkout redirects to login for guests
- [x] Test guest cart functionality
- [x] Fix AddToCartView redirect to cart instead of product list
- [x] Merge guest cart with user cart upon login (optional enhancement)
- [x] Implement guest checkout without login
  - [x] Modify CheckoutView in e_commerce/views.py to handle GET requests: Render checkout template showing cart items and form for guest details
  - [x] Modify CheckoutView to handle POST requests: Validate form, check stock, create OnlineOrder with guest fields, create OrderItems, clear session cart, redirect to order detail
  - [x] Create e_commerce/templates/e_commerce/checkout.html template with cart summary and checkout form
  - [ ] For authenticated users, keep current logic but add confirmation form if needed
- [ ] Test guest checkout functionality
- [ ] Ensure stock validation before order creation
- [ ] Handle order confirmation and email notifications if needed
