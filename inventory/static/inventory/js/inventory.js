// Inventory Module JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation
    initializeFormValidation();

    // Initialize form enhancements
    initializeFormEnhancements();

    // Initialize tooltips if Bootstrap tooltips are available
    initializeTooltips();

    // Initialize form progress
    initializeFormProgress();

    // Initialize page load animations
    initializePageAnimations();
});

function initializeFormValidation() {
    const forms = document.querySelectorAll('.inventory-form');

    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(form)) {
                event.preventDefault();
                event.stopPropagation();
            } else {
                // Show loading state
                showLoadingState(form);
            }
            form.classList.add('was-validated');
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });

            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });

    // Custom validations
    const skuField = form.querySelector('[name="sku"]');
    if (skuField && !validateSKU(skuField)) {
        isValid = false;
    }

    const priceField = form.querySelector('[name="unit_price"]');
    if (priceField && !validatePrice(priceField)) {
        isValid = false;
    }

    const reorderLevelField = form.querySelector('[name="reorder_level"]');
    if (reorderLevelField && !validateReorderLevel(reorderLevelField)) {
        isValid = false;
    }

    return isValid;
}

function validateField(field) {
    let isValid = true;
    const value = field.value.trim();
    const fieldName = field.name;

    // Clear previous validation
    field.classList.remove('is-invalid', 'is-valid');
    const feedback = field.parentNode.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.remove();
    }

    // Required field validation
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, `${getFieldLabel(field)} is required.`);
        isValid = false;
    }
    // Length validations
    else if (fieldName === 'name' && value.length < 2) {
        showFieldError(field, 'Name must be at least 2 characters long.');
        isValid = false;
    }
    else if (fieldName === 'description' && value.length > 500) {
        showFieldError(field, 'Description must be less than 500 characters.');
        isValid = false;
    }
    else if (value) {
        field.classList.add('is-valid');
    }

    return isValid;
}

function validateSKU(field) {
    const value = field.value.trim();
    const skuRegex = /^[A-Z0-9\-]+$/;

    if (value && !skuRegex.test(value)) {
        showFieldError(field, 'SKU must contain only uppercase letters, numbers, and hyphens.');
        return false;
    }

    return true;
}

function validatePrice(field) {
    const value = parseFloat(field.value);

    if (isNaN(value) || value < 0) {
        showFieldError(field, 'Please enter a valid positive price.');
        return false;
    }

    return true;
}

function validateReorderLevel(field) {
    const value = parseInt(field.value);

    if (isNaN(value) || value < 0) {
        showFieldError(field, 'Reorder level must be a non-negative integer.');
        return false;
    }

    return true;
}

function showFieldError(field, message) {
    field.classList.add('is-invalid');

    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;

    field.parentNode.appendChild(feedback);
}

function getFieldLabel(field) {
    const label = document.querySelector(`label[for="${field.id}"]`);
    return label ? label.textContent.replace('*', '').trim() : field.name;
}

function showLoadingState(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.innerHTML = '<span class="inventory-spinner"></span> Saving...';
        submitBtn.disabled = true;
        form.classList.add('inventory-loading');
    }
}

function initializeFormEnhancements() {
    // Auto-generate SKU for products
    const nameField = document.querySelector('[name="name"]');
    const skuField = document.querySelector('[name="sku"]');

    if (nameField && skuField && !skuField.value) {
        nameField.addEventListener('input', function() {
            const name = this.value.trim();
            if (name) {
                const generatedSKU = name.toUpperCase().replace(/[^A-Z0-9]/g, '-').substring(0, 10);
                skuField.value = generatedSKU;
                validateField(skuField);
            }
        });
    }

    // Format price input
    const priceField = document.querySelector('[name="unit_price"]');
    if (priceField) {
        priceField.addEventListener('input', function() {
            let value = this.value.replace(/[^0-9.]/g, '');
            const parts = value.split('.');
            if (parts.length > 2) {
                value = parts[0] + '.' + parts.slice(1).join('');
            }
            this.value = value;
        });
    }

    // Confirm before canceling
    const cancelLinks = document.querySelectorAll('a[href*="cancel"], a[href*="list"]');
    cancelLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            const form = document.querySelector('.inventory-form');
            const hasChanges = checkForChanges(form);

            if (hasChanges && !confirm('You have unsaved changes. Are you sure you want to leave?')) {
                event.preventDefault();
            }
        });
    });
}

function checkForChanges(form) {
    const inputs = form.querySelectorAll('input, select, textarea');
    for (let input of inputs) {
        if (input.value !== input.defaultValue) {
            return true;
        }
    }
    return false;
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips if available
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Utility function to show success message
function showSuccessMessage(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.inventory-form-container') || document.body;
    container.insertBefore(alert, container.firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

function initializeFormProgress() {
    const form = document.querySelector('.inventory-form');
    const progressBar = document.getElementById('formProgress');

    if (form && progressBar) {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        const totalFields = inputs.length;

        function updateProgress() {
            let filledFields = 0;
            inputs.forEach(input => {
                if (input.value.trim() !== '') {
                    filledFields++;
                }
            });
            const progress = (filledFields / totalFields) * 100;
            progressBar.style.width = progress + '%';
        }

        // Update progress on input
        inputs.forEach(input => {
            input.addEventListener('input', updateProgress);
            input.addEventListener('change', updateProgress);
        });

        // Initial progress update
        updateProgress();
    }
}

function initializePageAnimations() {
    // Add animation classes to form groups
    const formGroups = document.querySelectorAll('.inventory-form-group');
    formGroups.forEach((group, index) => {
        group.style.animationDelay = (index * 0.1) + 's';
        group.classList.add('animate-in');
    });
}

// Enhanced validation with animations
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');

    // Shake animation for invalid fields
    field.style.animation = 'shake 0.5s ease-in-out';

    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    feedback.textContent = message;
    feedback.style.animation = 'slideIn 0.3s ease-out';

    field.parentNode.appendChild(feedback);

    // Remove animation after it completes
    setTimeout(() => {
        field.style.animation = '';
    }, 500);
}

// Override the original validateField to include animations
const originalValidateField = validateField;
function validateField(field) {
    const result = originalValidateField(field);

    if (result && field.value.trim() !== '') {
        field.classList.add('is-valid');
        field.classList.remove('is-invalid');
        // Success animation
        field.style.animation = 'bounceIn 0.5s ease-out';
        setTimeout(() => {
            field.style.animation = '';
        }, 500);
    }

    return result;
}
