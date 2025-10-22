document.addEventListener('DOMContentLoaded', function() {
    // Initialize select2 for multi-select fields if available
    if (typeof $ !== 'undefined' && $.fn.select2) {
        $('#id_allowed_stores').select2({
            placeholder: 'Select stores...',
            allowClear: true
        });
        $('#id_allowed_departments').select2({
            placeholder: 'Select departments...',
            allowClear: true
        });
    }

    // Auto-calculate duration when times change
    function updateDuration() {
        const startTime = document.getElementById('id_start_time').value;
        const endTime = document.getElementById('id_end_time').value;

        if (startTime && endTime) {
            const start = new Date(`2000-01-01T${startTime}`);
            const end = new Date(`2000-01-01T${endTime}`);

            let duration = (end - start) / (1000 * 60 * 60); // hours
            if (duration < 0) {
                duration += 24; // Handle overnight shifts
            }

            // You could display this somewhere or just let the backend calculate it
            console.log(`Calculated duration: ${duration.toFixed(2)} hours`);
        }
    }

    const startTimeInput = document.getElementById('id_start_time');
    const endTimeInput = document.getElementById('id_end_time');

    if (startTimeInput) {
        startTimeInput.addEventListener('change', updateDuration);
    }
    if (endTimeInput) {
        endTimeInput.addEventListener('change', updateDuration);
    }

    console.log('Shift form enhancements initialized');
});
