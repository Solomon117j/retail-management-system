# UI Kit Documentation

## Overview

The UI Kit provides a comprehensive set of reusable CSS classes and JavaScript utilities for consistent styling and enhanced user interactions across the Retail Management System.

## File Structure

```
static/css/uikit/
├── variables.css    # CSS custom properties and design tokens
├── utilities.css    # Utility classes for spacing, typography, etc.
├── buttons.css      # Button component styles
├── components.css   # Complex component styles (cards, modals, etc.)
└── README.md        # This documentation

static/js/uikit/
└── uikit.js         # JavaScript utilities and enhancements
```

## CSS Variables

The UI Kit uses CSS custom properties for consistent theming. All colors, spacing, and other design tokens are defined in `variables.css`.

### Color Palette

```css
/* Primary Colors */
--primary-color: #007bff;
--primary-hover: #0056b3;
--primary-light: #e3f2fd;

/* Secondary Colors */
--secondary-color: #6c757d;
--secondary-hover: #545b62;

/* Success, Danger, Warning, Info colors available */
```

### Spacing

```css
--spacing-xs: 0.25rem;
--spacing-sm: 0.5rem;
--spacing-md: 1rem;
--spacing-lg: 1.5rem;
--spacing-xl: 2rem;
```

## Utility Classes

### Spacing

```html
<!-- Margin -->
<div class="m-3">Margin all sides</div>
<div class="mt-2">Margin top</div>
<div class="mb-4">Margin bottom</div>

<!-- Padding -->
<div class="p-2">Padding all sides</div>
<div class="pt-3">Padding top</div>
<div class="pb-1">Padding bottom</div>
```

### Text

```html
<div class="text-center">Centered text</div>
<div class="text-primary">Primary color text</div>
<div class="text-lg">Large text</div>
<div class="font-bold">Bold text</div>
```

### Display & Flexbox

```html
<div class="d-flex">Flex container</div>
<div class="justify-center">Center items</div>
<div class="align-center">Align items center</div>
```

### Borders & Shadows

```html
<div class="border">Border</div>
<div class="rounded">Rounded corners</div>
<div class="shadow">Shadow</div>
```

## Components

### Buttons

```html
<button class="btn">Default Button</button>
<button class="btn btn-primary">Primary Button</button>
<button class="btn btn-success">Success Button</button>
<button class="btn btn-danger">Danger Button</button>
<button class="btn btn-outline-primary">Outline Button</button>
```

### Cards

```html
<div class="card">
    <div class="card-header">Card Title</div>
    <div class="card-body">
        <p>Card content goes here.</p>
    </div>
    <div class="card-footer">Card footer</div>
</div>
```

### Alerts

```html
<div class="alert alert-primary">Primary alert</div>
<div class="alert alert-success">Success alert</div>
<div class="alert alert-danger">Danger alert</div>
<div class="alert alert-warning">Warning alert</div>
```

### Forms

```html
<form class="needs-validation">
    <div class="form-group">
        <label class="form-label">Email</label>
        <input type="email" class="form-control" required>
    </div>
    <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

### Tables

```html
<table class="table table-striped">
    <thead>
        <tr>
            <th>Name</th>
            <th>Email</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>John Doe</td>
            <td>john@example.com</td>
        </tr>
    </tbody>
</table>
```

## JavaScript Utilities

### Initialization

The UI Kit automatically initializes when the DOM is loaded:

```javascript
document.addEventListener('DOMContentLoaded', () => {
    window.uiKit = new UIKit();
});
```

### Toast Notifications

```javascript
// Show a success toast
UIKit.showToast('Operation completed successfully!', 'success');

// Show an error toast
UIKit.showToast('An error occurred!', 'danger');
```

### Loading Spinners

```javascript
// Show spinner on button
const button = document.querySelector('#submit-btn');
UIKit.showSpinner(button);

// Hide spinner
UIKit.hideSpinner(button);
```

### Confirm Dialog

```javascript
UIKit.confirm('Are you sure you want to delete this item?')
    .then(confirmed => {
        if (confirmed) {
            // Delete the item
        }
    });
```

## Integration

### Include in Templates

Add the UI Kit CSS files to your base template:

```html
<!-- UI Kit CSS -->
<link rel="stylesheet" href="{% static 'css/uikit/variables.css' %}">
<link rel="stylesheet" href="{% static 'css/uikit/utilities.css' %}">
<link rel="stylesheet" href="{% static 'css/uikit/buttons.css' %}">
<link rel="stylesheet" href="{% static 'css/uikit/components.css' %}">

<!-- UI Kit JavaScript -->
<script src="{% static 'js/uikit/uikit.js' %}"></script>
```

### Using with Bootstrap

The UI Kit is designed to work alongside Bootstrap 5.1.3. It extends Bootstrap's functionality while maintaining compatibility.

### Customizing

To customize the UI Kit:

1. Modify variables in `variables.css`
2. Add custom styles in your theme CSS file
3. Extend the UIKit class for additional JavaScript functionality

## Best Practices

1. **Use semantic class names**: Prefer utility classes for rapid development
2. **Consistent spacing**: Use the predefined spacing scale
3. **Color consistency**: Always use the defined color variables
4. **Responsive design**: Combine with Bootstrap's responsive utilities
5. **Accessibility**: Maintain proper contrast ratios and semantic HTML

## Examples

### Complete Form Example

```html
<div class="card">
    <div class="card-header">Contact Form</div>
    <div class="card-body">
        <form class="needs-validation">
            <div class="form-group mb-3">
                <label class="form-label">Name</label>
                <input type="text" class="form-control" required>
            </div>
            <div class="form-group mb-3">
                <label class="form-label">Email</label>
                <input type="email" class="form-control" required>
            </div>
            <div class="d-flex justify-end">
                <button type="submit" class="btn btn-primary">Submit</button>
            </div>
        </form>
    </div>
</div>
```

### Interactive Button with Loading

```html
<button class="btn btn-primary" onclick="handleSubmit(this)">
    <span class="btn-text">Submit</span>
</button>

<script>
function handleSubmit(button) {
    UIKit.showSpinner(button);
    button.querySelector('.btn-text').textContent = 'Processing...';

    // Simulate async operation
    setTimeout(() => {
        UIKit.hideSpinner(button);
        button.querySelector('.btn-text').textContent = 'Submit';
        UIKit.showToast('Form submitted successfully!', 'success');
    }, 2000);
}
</script>
```

## Migration Guide

### From Inline Styles

Replace inline styles with UI Kit classes:

```html
<!-- Before -->
<div style="margin: 1rem; padding: 0.5rem; color: #007bff;">Content</div>

<!-- After -->
<div class="m-3 p-2 text-primary">Content</div>
```

### From Bootstrap Classes

The UI Kit extends Bootstrap, so existing Bootstrap classes continue to work:

```html
<!-- This still works -->
<button class="btn btn-primary">Button</button>

<!-- Enhanced with UI Kit -->
<button class="btn btn-primary shadow">Button</button>
```

## Support

For questions or issues with the UI Kit:

1. Check this documentation first
2. Review the CSS and JavaScript source files
3. Test in different browsers
4. Ensure proper loading order of CSS files

## Version History

- **v1.0.0**: Initial release with core components and utilities
- Comprehensive CSS variables system
- JavaScript utilities for enhanced UX
- Bootstrap 5.1.3 compatibility
