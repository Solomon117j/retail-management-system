document.addEventListener('DOMContentLoaded', function() {
    const shiftSelect = document.getElementById('id_shift');
    const previewDiv = document.getElementById('shift-preview');
    const noShiftDiv = document.getElementById('no-shift-selected');
    const form = document.querySelector('form');
    const submitBtn = form.querySelector('button[type="submit"]');

    // Shift data (passed from view)
    const shiftsData = JSON.parse('{{ shifts_json|default:"{}"|escapejs }}');

    function updateShiftPreview() {
        const shiftId = shiftSelect.value;
        if (shiftId && shiftsData[shiftId]) {
            const shift = shiftsData[shiftId];
            document.getElementById('shift-name').textContent = shift.name;
            document.getElementById('shift-type').textContent = shift.shift_type_display;
            document.getElementById('shift-time').textContent = shift.start_time + ' - ' + shift.end_time;
            document.getElementById('shift-duration').textContent = shift.duration_hours ? shift.duration_hours + ' hours' : 'Duration not set';

            // Enhanced preview: add break info if available
            const breakInfo = document.getElementById('shift-break');
            if (breakInfo) {
                breakInfo.textContent = shift.break_duration ? `Break: ${shift.break_duration} minutes` : 'No break scheduled';
            }

            previewDiv.style.display = 'block';
            noShiftDiv.style.display = 'none';
        } else {
            previewDiv.style.display = 'none';
            noShiftDiv.style.display = 'block';
        }
    }

    if (shiftSelect) {
        shiftSelect.addEventListener('change', updateShiftPreview);
        // Initial preview update
        updateShiftPreview();
    }

    // Date validation - prevent past dates
    const dateInput = document.getElementById('id_date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
        dateInput.setAttribute('aria-describedby', 'date-help');
    }

    // Client-side form validation
    function validateForm() {
        let isValid = true;
        const errors = [];

        // Required fields
        const requiredFields = ['id_employee', 'id_shift', 'id_date', 'id_status'];
        requiredFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field && !field.value.trim()) {
                field.classList.add('is-invalid');
                errors.push(`${field.previousElementSibling.textContent} is required.`);
                isValid = false;
            } else if (field) {
                field.classList.remove('is-invalid');
            }
        });

        // Date validation
        const selectedDate = new Date(dateInput.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        if (selectedDate < today) {
            dateInput.classList.add('is-invalid');
            errors.push('Date cannot be in the past.');
            isValid = false;
        }

        // Display errors
        const errorContainer = document.getElementById('form-errors');
        if (errorContainer) {
            errorContainer.innerHTML = errors.map(error => `<div class="alert alert-danger">${error}</div>`).join('');
            errorContainer.style.display = errors.length ? 'block' : 'none';
        }

        return isValid;
    }

    // Submit confirmation
    function confirmSubmit() {
        const employeeName = document.getElementById('id_employee').selectedOptions[0]?.text || 'Unknown';
        const shiftName = shiftSelect.selectedOptions[0]?.text || 'Unknown';
        const date = dateInput.value;
        return confirm(`Confirm scheduling ${employeeName} for ${shiftName} on ${date}?`);
    }

    // Form submit handler
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            return false;
        }
        if (!confirmSubmit()) {
            e.preventDefault();
            return false;
        }
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Saving...';
    });

    // Quick Actions with feedback
    const quickActions = [
        {
            id: 'set-today',
            action: () => {
                const today = new Date().toISOString().split('T')[0];
                document.getElementById('id_date').value = today;
                showFeedback('Date set to today');
            },
            tooltip: 'Set date to today'
        },
        {
            id: 'set-scheduled',
            action: () => {
                const statusSelect = document.getElementById('id_status');
                if (statusSelect) {
                    for (let option of statusSelect.options) {
                        if (option.value.toLowerCase().includes('scheduled')) {
                            statusSelect.value = option.value;
                            showFeedback('Status set to Scheduled');
                            break;
                        }
                    }
                }
            },
            tooltip: 'Set status to Scheduled'
        },
        {
            id: 'clear-custom-times',
            action: () => {
                const startTime = document.getElementById('id_custom_start_time');
                const endTime = document.getElementById('id_custom_end_time');
                if (startTime) startTime.value = '';
                if (endTime) endTime.value = '';
                showFeedback('Custom times cleared');
            },
            tooltip: 'Clear custom start and end times'
        }
    ];

    quickActions.forEach(({ id, action, tooltip }) => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.setAttribute('title', tooltip);
            btn.setAttribute('aria-label', tooltip);
            btn.addEventListener('click', action);
        }
    });

    // Feedback function
    function showFeedback(message) {
        const feedback = document.createElement('div');
        feedback.className = 'alert alert-success alert-dismissible fade show position-fixed';
        feedback.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
        feedback.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(feedback);
        setTimeout(() => feedback.remove(), 3000);
    }

    // Accessibility: Keyboard navigation for quick actions
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            form.requestSubmit();
        }
    });

    console.log('Schedule form enhancements initialized with improvements');
});
