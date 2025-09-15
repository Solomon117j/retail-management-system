/**
 * UI Kit JavaScript Utilities
 * Provides enhanced functionality for UI components
 */

class UIKit {
    constructor() {
        this.init();
    }

    init() {
        this.initDropdowns();
        this.initModals();
        this.initAlerts();
        this.initTooltips();
        this.initForms();
    }

    // Enhanced Dropdown Functionality
    initDropdowns() {
        const subMenus = document.querySelectorAll('.dropdown-submenu');

        subMenus.forEach(subMenu => {
            const toggle = subMenu.querySelector('.dropdown-toggle');
            const menu = subMenu.querySelector('.dropdown-menu');

            if (toggle && menu) {
                toggle.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();

                    // Hide other sub-menus
                    subMenus.forEach(otherSubMenu => {
                        if (otherSubMenu !== subMenu) {
                            const otherMenu = otherSubMenu.querySelector('.dropdown-menu');
                            if (otherMenu) otherMenu.classList.remove('show');
                        }
                    });

                    // Toggle current sub-menu
                    menu.classList.toggle('show');
                });
            }
        });

        // Close sub-menus when clicking outside
        document.addEventListener('click', (e) => {
            const inventoryDropdown = document.getElementById('inventoryDropdown');
            if (inventoryDropdown && !inventoryDropdown.contains(e.target)) {
                subMenus.forEach(subMenu => {
                    const menu = subMenu.querySelector('.dropdown-menu');
                    if (menu) menu.classList.remove('show');
                });
            }
        });
    }

    // Modal Management
    initModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('shown.bs.modal', () => {
                const firstInput = modal.querySelector('input, textarea, select');
                if (firstInput) firstInput.focus();
            });
        });
    }

    // Alert Management
    initAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        });
    }

    // Tooltip Initialization
    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }

    // Form Enhancements
    initForms() {
        const forms = document.querySelectorAll('.needs-validation');
        forms.forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    }

    // Utility Methods
    static showSpinner(element) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        spinner.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"><span class="sr-only">Loading...</span></div>';

        if (element) {
            element.appendChild(spinner);
            element.classList.add('loading');
        }

        return spinner;
    }

    static hideSpinner(element) {
        if (element) {
            const spinner = element.querySelector('.spinner');
            if (spinner) spinner.remove();
            element.classList.remove('loading');
        }
    }

    static showToast(message, type = 'info', duration = 3000) {
        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            const container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        document.querySelector('.toast-container').appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { delay: duration });
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => toast.remove());
    }
}

// Initialize UIKit when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.uiKit = new UIKit();
});
