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
