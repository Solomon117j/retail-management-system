/**
 * RETAIL MANAGEMENT SYSTEM - MAIN JAVASCRIPT
 * Shared JavaScript functionality across all apps
 */

// ========================================
// GLOBAL VARIABLES AND CONFIGURATION
// ========================================
const RMS = {
    // Configuration
    config: {
        animationDuration: 300,
        toastDuration: 5000,
        confirmationTimeout: 10000
    },
    
    // Utility functions
    utils: {},
    
    // Module-specific functions
    modules: {
        inventory: {},
        sales: {},
        hr: {},
        procurement: {},
        ecommerce: {}
    }
};

// ========================================
// UTILITY FUNCTIONS
// ========================================

/**
 * Show a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of toast (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
RMS.utils.showToast = function(message, type = 'info', duration = RMS.config.toastDuration) {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast-notification');
    existingToasts.forEach(toast => toast.remove());
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast-notification alert alert-${type} alert-dismissible fade show`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (toast.parentNode) {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
};

/**
 * Show a confirmation dialog
 * @param {string} message - The confirmation message
 * @param {function} onConfirm - Callback function when confirmed
 * @param {function} onCancel - Callback function when cancelled
 */
RMS.utils.showConfirmation = function(message, onConfirm, onCancel = null) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Confirmation</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-danger" id="confirm-action">Confirm</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
    
    // Handle confirmation
    modal.querySelector('#confirm-action').addEventListener('click', () => {
        bootstrapModal.hide();
        if (onConfirm) onConfirm();
    });
    
    // Handle cancellation
    modal.addEventListener('hidden.bs.modal', () => {
        if (onCancel) onCancel();
        modal.remove();
    });
};

/**
 * Format currency values
 * @param {number} amount - The amount to format
 * @param {string} currency - Currency code (default: USD)
 */
RMS.utils.formatCurrency = function(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
};

/**
 * Format dates
 * @param {string|Date} date - The date to format
 * @param {string} format - Format type (short, long, time)
 */
RMS.utils.formatDate = function(date, format = 'short') {
    const dateObj = new Date(date);
    const options = {
        short: { year: 'numeric', month: 'short', day: 'numeric' },
        long: { year: 'numeric', month: 'long', day: 'numeric' },
        time: { hour: '2-digit', minute: '2-digit' }
    };
    
    return dateObj.toLocaleDateString('en-US', options[format]);
};

/**
 * Debounce function for search inputs
 * @param {function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 */
RMS.utils.debounce = function(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

/**
 * Show loading state on element
 * @param {HTMLElement} element - Element to show loading on
 */
RMS.utils.showLoading = function(element) {
    element.classList.add('loading');
    element.disabled = true;
};

/**
 * Hide loading state on element
 * @param {HTMLElement} element - Element to hide loading on
 */
RMS.utils.hideLoading = function(element) {
    element.classList.remove('loading');
    element.disabled = false;
};

// ========================================
// FORM HANDLING
// ========================================

/**
 * Handle AJAX form submissions
 * @param {HTMLFormElement} form - The form element
 * @param {object} options - Configuration options
 */
RMS.utils.handleAjaxForm = function(form, options = {}) {
    const defaults = {
        showLoading: true,
        showSuccess: true,
        showErrors: true,
        resetOnSuccess: false
    };
    
    const config = { ...defaults, ...options };
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (config.showLoading && submitBtn) {
            RMS.utils.showLoading(submitBtn);
        }
        
        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: form.method,
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                if (config.showSuccess) {
                    RMS.utils.showToast(data.message || 'Operation completed successfully!', 'success');
                }
                
                if (config.resetOnSuccess) {
                    form.reset();
                }
                
                if (config.onSuccess) {
                    config.onSuccess(data);
                }
            } else {
                if (config.showErrors) {
                    RMS.utils.showToast(data.message || 'An error occurred', 'danger');
                }
                
                if (config.onError) {
                    config.onError(data);
                }
            }
        } catch (error) {
            console.error('Form submission error:', error);
            if (config.showErrors) {
                RMS.utils.showToast('Network error occurred', 'danger');
            }
        } finally {
            if (config.showLoading && submitBtn) {
                RMS.utils.hideLoading(submitBtn);
            }
        }
    });
};

// ========================================
// TABLE ENHANCEMENTS
// ========================================

/**
 * Add search functionality to tables
 * @param {HTMLTableElement} table - The table element
 * @param {HTMLInputElement} searchInput - The search input element
 */
RMS.utils.addTableSearch = function(table, searchInput) {
    const debouncedSearch = RMS.utils.debounce((searchTerm) => {
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const matches = text.includes(searchTerm.toLowerCase());
            row.style.display = matches ? '' : 'none';
        });
    }, 300);
    
    searchInput.addEventListener('input', (e) => {
        debouncedSearch(e.target.value);
    });
};

/**
 * Add sorting functionality to tables
 * @param {HTMLTableElement} table - The table element
 */
RMS.utils.addTableSorting = function(table) {
    const headers = table.querySelectorAll('thead th[data-sortable]');
    
    headers.forEach(header => {
        header.style.cursor = 'pointer';
        header.innerHTML += ' <i class="fas fa-sort text-muted"></i>';
        
        header.addEventListener('click', () => {
            const column = header.dataset.sortable;
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            // Determine sort direction
            const currentSort = header.dataset.sortDirection || 'asc';
            const newSort = currentSort === 'asc' ? 'desc' : 'asc';
            
            // Update header icons
            headers.forEach(h => {
                h.querySelector('i').className = 'fas fa-sort text-muted';
                delete h.dataset.sortDirection;
            });
            
            header.dataset.sortDirection = newSort;
            header.querySelector('i').className = `fas fa-sort-${newSort === 'asc' ? 'up' : 'down'} text-primary`;
            
            // Sort rows
            rows.sort((a, b) => {
                const aVal = a.querySelector(`[data-sort="${column}"]`)?.textContent || '';
                const bVal = b.querySelector(`[data-sort="${column}"]`)?.textContent || '';
                
                const comparison = aVal.localeCompare(bVal, undefined, { numeric: true });
                return newSort === 'asc' ? comparison : -comparison;
            });
            
            // Reorder rows
            rows.forEach(row => tbody.appendChild(row));
        });
    });
};

// ========================================
// MODULE-SPECIFIC FUNCTIONS
// ========================================

// Inventory Module Functions
RMS.modules.inventory = {
    /**
     * Update stock quantity with visual feedback
     */
    updateStock: function(productId, newQuantity) {
        // Implementation for stock updates
        console.log(`Updating stock for product ${productId} to ${newQuantity}`);
    },
    
    /**
     * Check low stock items
     */
    checkLowStock: function() {
        const lowStockItems = document.querySelectorAll('.inventory-item.low-stock');
        if (lowStockItems.length > 0) {
            RMS.utils.showToast(`${lowStockItems.length} items are low in stock`, 'warning');
        }
    }
};

// Sales Module Functions
RMS.modules.sales = {
    /**
     * Calculate total for sales form
     */
    calculateTotal: function() {
        const quantityInputs = document.querySelectorAll('[name*="quantity"]');
        const priceInputs = document.querySelectorAll('[name*="price"]');
        let total = 0;
        
        quantityInputs.forEach((qtyInput, index) => {
            const qty = parseFloat(qtyInput.value) || 0;
            const price = parseFloat(priceInputs[index]?.value) || 0;
            total += qty * price;
        });
        
        const totalElement = document.querySelector('#total-amount');
        if (totalElement) {
            totalElement.textContent = RMS.utils.formatCurrency(total);
        }
    }
};

// HR Module Functions
RMS.modules.hr = {
    /**
     * Update attendance status with color coding
     */
    updateAttendanceStatus: function(employeeId, status) {
        const statusElement = document.querySelector(`[data-employee="${employeeId}"] .attendance-status`);
        if (statusElement) {
            statusElement.className = `attendance-status attendance-${status}`;
            statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        }
    }
};

// ========================================
// INITIALIZATION
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Initialize table enhancements
    const searchableTable = document.querySelector('.table[data-searchable]');
    const searchInput = document.querySelector('#table-search');
    if (searchableTable && searchInput) {
        RMS.utils.addTableSearch(searchableTable, searchInput);
    }
    
    const sortableTable = document.querySelector('.table[data-sortable]');
    if (sortableTable) {
        RMS.utils.addTableSorting(sortableTable);
    }
    
    // Initialize AJAX forms
    const ajaxForms = document.querySelectorAll('.ajax-form');
    ajaxForms.forEach(form => {
        RMS.utils.handleAjaxForm(form);
    });
    
    // Add confirmation to delete buttons
    const deleteButtons = document.querySelectorAll('.btn-delete, .delete-btn');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const itemName = this.dataset.itemName || 'this item';
            RMS.utils.showConfirmation(
                `Are you sure you want to delete ${itemName}? This action cannot be undone.`,
                () => {
                    // If it's a form, submit it; if it's a link, follow it
                    if (this.closest('form')) {
                        this.closest('form').submit();
                    } else {
                        window.location.href = this.href;
                    }
                }
            );
        });
    });
    
    // Module-specific initializations
    if (document.body.classList.contains('inventory-page')) {
        RMS.modules.inventory.checkLowStock();
    }
    
    if (document.body.classList.contains('sales-page')) {
        // Initialize sales calculations
        const quantityInputs = document.querySelectorAll('[name*="quantity"]');
        const priceInputs = document.querySelectorAll('[name*="price"]');
        
        [...quantityInputs, ...priceInputs].forEach(input => {
            input.addEventListener('input', RMS.modules.sales.calculateTotal);
        });
    }
    
    console.log('Retail Management System JavaScript initialized');
});

// ========================================
// GLOBAL ERROR HANDLING
// ========================================

window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    RMS.utils.showToast('An unexpected error occurred', 'danger');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    RMS.utils.showToast('An unexpected error occurred', 'danger');
});

// Export RMS object for use in other scripts
window.RMS = RMS;