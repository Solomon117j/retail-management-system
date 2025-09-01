# TODO: Implement Quick Actions and Data Exports for Customers

## Step 1: Add Cart Models
- [x] Add Cart and CartItem models to e_commerce/models.py

## Step 2: Create Cart Views
- [x] Add AddToCartView, CartView, RemoveFromCartView, CheckoutView to e_commerce/views.py

## Step 3: Add Export View
- [x] Add OrderExportView to e_commerce/views.py for CSV export

## Step 4: Update URLs
- [x] Add new URLs for cart and export in e_commerce/urls.py

## Step 5: Update Templates
- [x] Update product_list.html: add form for add to cart with quantity
- [x] Update product_detail.html: add form for add to cart with quantity
- [x] Update order_list.html: add export button
- [x] Create cart.html template
- [x] Create checkout.html template

## Step 6: Run Migrations
- [x] Create and run migrations for new Cart and CartItem models

## Step 7: Test Functionality
- [ ] Test add to cart, view cart, checkout
- [ ] Test order export to CSV
- [ ] Ensure authentication works for customers

# TODO: Fix Missing Fields in Product Form

## Step 1: Identify Missing Fields
- [x] Found 'available_online' and 'image' fields missing from product_form.html template

## Step 2: Update Template
- [x] Add 'available_online' checkbox and 'image' file input to inventory/templates/inventory/product_form.html

## Step 3: Test Form
- [ ] Test the product form to ensure 'available_online' and 'image' fields appear and function correctly

# TODO: Indicate Online Orders in Staff Portal

## Step 1: Update Dashboard View
- [x] Add recent_online_orders queryset to DashboardView in dashboards/views.py

## Step 2: Update Dashboard Template
- [x] Add Recent Online Orders section to templates/dashboard/index.html with table showing order details and status badges

## Step 3: Test Implementation
- [ ] Test that recent online orders appear on staff dashboard
- [ ] Verify status badges display correctly (pending=warning, processing=info)
- [ ] Confirm links to order details work properly

# TODO: Improve Staff Order Form

## Step 1: Enhance Form Styling
- [x] Add proper Bootstrap classes to form fields and layout
- [x] Improve visual hierarchy and spacing

## Step 2: Fix JavaScript Functionality
- [x] Fix store pickup toggle JavaScript
- [x] Add dynamic order item addition/removal
- [x] Add client-side total calculation

## Step 3: Improve User Experience
- [x] Add form validation feedback styling
- [x] Add loading states and better error handling
- [x] Add autocomplete for product selection

## Step 4: Test Enhanced Form
- [ ] Test all form functionality including dynamic items
- [ ] Verify JavaScript works correctly
- [ ] Test form validation and error display

# TODO: Improve Order Form Styling

## Step 1: Include E-commerce CSS
- [x] Add e_commerce.css link to order_form.html template

## Step 2: Update HTML Classes
- [ ] Replace Bootstrap classes with enhanced e-commerce classes
- [ ] Add custom classes for form sections and elements

## Step 3: Enhance CSS Styles
- [ ] Add specific styles for order form components
- [ ] Improve button styling and interactions
- [ ] Add animations and transitions

## Step 4: Improve Responsiveness
- [ ] Enhance mobile layout and spacing
- [ ] Optimize form for different screen sizes

## Step 5: Test Enhanced Styling
- [ ] Verify visual improvements in browser
- [ ] Test JavaScript functionality with new styles
- [ ] Check mobile responsiveness
