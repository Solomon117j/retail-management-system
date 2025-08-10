# Shared Styles Guide

This guide explains how to use the shared CSS and JavaScript files across all Django apps in the retail management system.

## 📁 File Structure

```
retail_management_system/
├── static/
│   ├── css/
│   │   └── main.css          # Main shared stylesheet
│   ├── js/
│   │   └── main.js           # Main shared JavaScript
│   └── images/               # Shared images
├── templates/
│   └── base.html             # Base template with shared styles
└── [individual apps]/
    └── templates/            # App-specific templates
```

## 🎨 CSS Features

### 1. CSS Custom Properties (Variables)
The main.css file uses CSS custom properties for consistent theming:

```css
:root {
    --primary-color: #007bff;
    --brand-primary: #2c3e50;
    --spacing-md: 1rem;
    --border-radius-lg: 0.5rem;
}
```

### 2. Pre-built Component Classes

#### Dashboard Cards
```html
<div class="card dashboard-card h-100">
    <div class="card-body text-center">
        <i class="fas fa-store fa-3x mb-3 text-primary"></i>
        <h3 class="card-title">Store Management</h3>
        <p class="card-text">Manage stores and departments</p>
    </div>
</div>
```

#### Module-Specific Classes
```html
<!-- Inventory -->
<div class="inventory-item low-stock">...</div>
<div class="inventory-item out-of-stock">...</div>

<!-- HR -->
<div class="employee-card">...</div>
<span class="attendance-present">Present</span>
<span class="attendance-absent">Absent</span>

<!-- Sales -->
<div class="sales-summary">...</div>

<!-- Procurement -->
<div class="supplier-card">...</div>
<span class="order-status-pending">Pending</span>
```

#### Utility Classes
```html
<!-- Spacing -->
<div class="m-lg p-xl">Content with large margin and extra-large padding</div>

<!-- Colors -->
<span class="text-brand-primary">Brand colored text</span>
<div class="bg-brand-secondary">Brand colored background</div>

<!-- Shadows -->
<div class="shadow-lg">Element with large shadow</div>

<!-- Border Radius -->
<div class="rounded-xl">Element with extra-large border radius</div>
```

### 3. Responsive Design
All styles are mobile-first and responsive:

```css
/* Mobile first */
.dashboard-card .card-body {
    padding: var(--spacing-lg);
}

/* Tablet and up */
@media (min-width: 768px) {
    .dashboard-card:hover {
        transform: translateY(-8px);
    }
}
```

## 🚀 JavaScript Features

### 1. Global RMS Object
All functionality is organized under the `RMS` global object:

```javascript
// Show notifications
RMS.utils.showToast('Success message!', 'success');

// Show confirmations
RMS.utils.showConfirmation('Delete this item?', () => {
    // Confirmed action
});

// Format currency
const formatted = RMS.utils.formatCurrency(123.45); // "$123.45"

// Format dates
const formatted = RMS.utils.formatDate('2024-01-15', 'long');
```

### 2. Module-Specific Functions
```javascript
// Inventory functions
RMS.modules.inventory.updateStock(productId, newQuantity);
RMS.modules.inventory.checkLowStock();

// Sales functions
RMS.modules.sales.calculateTotal();

// HR functions
RMS.modules.hr.updateAttendanceStatus(employeeId, 'present');
```

### 3. Form Enhancements
```javascript
// AJAX form handling
const form = document.querySelector('#my-form');
RMS.utils.handleAjaxForm(form, {
    showLoading: true,
    showSuccess: true,
    resetOnSuccess: true
});
```

### 4. Table Enhancements
```html
<!-- Searchable table -->
<input type="text" id="table-search" placeholder="Search...">
<table class="table" data-searchable>
    <!-- table content -->
</table>

<!-- Sortable table -->
<table class="table" data-sortable>
    <thead>
        <tr>
            <th data-sortable="name">Name</th>
            <th data-sortable="price">Price</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td data-sort="name">Product A</td>
            <td data-sort="price">$10.00</td>
        </tr>
    </tbody>
</table>
```

## 🔧 How to Use in Your Apps

### 1. In Templates
Your app templates should extend the base template:

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}My App - {{ block.super }}{% endblock %}

{% block extra_css %}
    <!-- App-specific CSS if needed -->
    <link rel="stylesheet" href="{% static 'my_app/css/custom.css' %}">
{% endblock %}

{% block content %}
    <div class="container mt-4">
        <div class="card dashboard-card">
            <div class="card-body">
                <h2>My App Content</h2>
                <button class="btn btn-primary" onclick="RMS.utils.showToast('Hello!', 'info')">
                    Test Toast
                </button>
            </div>
        </div>
    </div>
{% endblock %}

{% block extra_js %}
    <!-- App-specific JavaScript if needed -->
    <script src="{% static 'my_app/js/custom.js' %}"></script>
{% endblock %}
```

### 2. Adding App-Specific Styles
If you need app-specific styles, create them in your app's static directory:

```
my_app/
├── static/
│   └── my_app/
│       ├── css/
│       │   └── custom.css
│       └── js/
│           └── custom.js
└── templates/
```

Then include them in your templates:
```html
{% block extra_css %}
    <link rel="stylesheet" href="{% static 'my_app/css/custom.css' %}">
{% endblock %}
```

### 3. Using CSS Variables in Custom Styles
```css
/* my_app/static/my_app/css/custom.css */
.my-custom-component {
    background-color: var(--brand-primary);
    padding: var(--spacing-lg);
    border-radius: var(--border-radius-md);
    box-shadow: var(--shadow-md);
}
```

## 🎯 Best Practices

### 1. CSS Organization
- Use the shared CSS variables for consistency
- Follow the existing naming conventions
- Add module-specific classes to main.css if they'll be reused
- Keep app-specific styles in separate files

### 2. JavaScript Organization
- Use the RMS namespace for global functions
- Add module-specific functions to `RMS.modules.yourModule`
- Initialize app-specific code in DOMContentLoaded event

### 3. Performance
- The shared files are loaded once and cached
- Use CSS custom properties for easy theming
- Minimize app-specific CSS/JS files

### 4. Maintenance
- Update shared styles in main.css for global changes
- Document any new utility classes or JavaScript functions
- Test changes across all apps

## 🔄 Updating Shared Styles

### Adding New CSS Variables
```css
:root {
    /* Add new variables here */
    --new-color: #123456;
    --new-spacing: 2rem;
}
```

### Adding New Utility Classes
```css
/* Add new utility classes */
.text-new-color { color: var(--new-color) !important; }
.spacing-new { margin: var(--new-spacing) !important; }
```

### Adding New JavaScript Functions
```javascript
// Add to RMS.utils for general utilities
RMS.utils.newUtilityFunction = function() {
    // Implementation
};

// Add to RMS.modules for module-specific functions
RMS.modules.newModule = {
    newFunction: function() {
        // Implementation
    }
};
```

## 🐛 Troubleshooting

### Styles Not Loading
1. Check that `{% load static %}` is at the top of your template
2. Verify STATICFILES_DIRS is configured in settings.py
3. Run `python manage.py collectstatic` for production

### JavaScript Errors
1. Check browser console for errors
2. Ensure Bootstrap is loaded before main.js
3. Verify RMS object is available: `console.log(window.RMS)`

### CSS Variables Not Working
1. Ensure you're using modern browsers (IE11+ support)
2. Check CSS syntax: `var(--variable-name)`
3. Verify variables are defined in :root

## 📱 Mobile Responsiveness

The shared styles include mobile-first responsive design:

```css
/* Mobile first (default) */
.card-body { padding: 1rem; }

/* Tablet and up */
@media (min-width: 768px) {
    .card-body { padding: 1.5rem; }
}

/* Desktop and up */
@media (min-width: 992px) {
    .card-body { padding: 2rem; }
}
```

## 🎨 Theming

To change the overall theme, update the CSS variables in main.css:

```css
:root {
    /* Change these for different themes */
    --brand-primary: #your-color;
    --brand-secondary: #your-color;
    --brand-accent: #your-color;
}
```

This will automatically update all components using these variables throughout the application.