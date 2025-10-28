// Enhanced Shift Form JavaScript with Modern Features
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Enhanced Shift Form initialized with modern features');

    // Utility functions
    const utils = {
        debounce: (func, wait) => {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        animate: (element, animation, duration = 300) => {
            element.style.animation = `${animation} ${duration}ms ease-in-out`;
            setTimeout(() => {
                element.style.animation = '';
            }, duration);
        },

        showNotification: (message, type = 'info') => {
            const notification = document.createElement('div');
            notification.className = `alert alert-${type} position-fixed`;
            notification.style.cssText = `
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                animation: slideInRight 0.5s ease-out;
            `;
            notification.innerHTML = `
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close float-end" onclick="this.parentElement.remove()"></button>
            `;
            document.body.appendChild(notification);
            setTimeout(() => notification.remove(), 5000);
        }
    };

    // Enhanced time validation with visual feedback
    function validateTimes() {
        const startTime = document.getElementById('id_start_time');
        const endTime = document.getElementById('id_end_time');
        const feedback = document.getElementById('time-validation-feedback');

        if (startTime && endTime && startTime.value && endTime.value) {
            const start = new Date(`2000-01-01T${startTime.value}`);
            const end = new Date(`2000-01-01T${endTime.value}`);

            if (end <= start) {
                endTime.setCustomValidity('End time must be after start time');
                endTime.classList.add('is-invalid');
                utils.showNotification('End time must be after start time', 'error');
                if (feedback) {
                    feedback.innerHTML = '<i class="fas fa-exclamation-triangle text-danger me-1"></i>End time must be after start time';
                    feedback.style.display = 'block';
                }
            } else {
                endTime.setCustomValidity('');
                endTime.classList.remove('is-invalid');
                if (feedback) {
                    feedback.innerHTML = '<i class="fas fa-check-circle text-success me-1"></i>Time range is valid';
                    feedback.style.display = 'block';
                    setTimeout(() => feedback.style.display = 'none', 3000);
                }
            }
        }
    }

    // Advanced JSON validation for break times with syntax highlighting
    function validateBreakTimes() {
        const breakTimesField = document.getElementById('id_break_times');
        const feedback = document.getElementById('break-validation-feedback');

        if (breakTimesField && breakTimesField.value.trim()) {
            try {
                const breaks = JSON.parse(breakTimesField.value);
                if (!Array.isArray(breaks)) {
                    throw new Error('Break times must be an array');
                }

                // Enhanced validation
                breaks.forEach((breakItem, index) => {
                    if (!breakItem.start || !breakItem.end) {
                        throw new Error(`Break ${index + 1}: Missing start or end time`);
                    }
                    if (!breakItem.type) {
                        breakItem.type = 'break';
                    }
                    // Validate time format
                    if (!/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/.test(breakItem.start) ||
                        !/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/.test(breakItem.end)) {
                        throw new Error(`Break ${index + 1}: Invalid time format (use HH:MM)`);
                    }
                });

                breakTimesField.setCustomValidity('');
                breakTimesField.classList.remove('is-invalid');
                if (feedback) {
                    feedback.innerHTML = '<i class="fas fa-check-circle text-success me-1"></i>JSON format is valid';
                    feedback.style.display = 'block';
                    setTimeout(() => feedback.style.display = 'none', 3000);
                }
            } catch (e) {
                breakTimesField.setCustomValidity(`Invalid JSON format: ${e.message}`);
                breakTimesField.classList.add('is-invalid');
                utils.showNotification(`Break times error: ${e.message}`, 'error');
                if (feedback) {
                    feedback.innerHTML = `<i class="fas fa-exclamation-triangle text-danger me-1"></i>${e.message}`;
                    feedback.style.display = 'block';
                }
            }
        } else {
            breakTimesField.setCustomValidity('');
            breakTimesField.classList.remove('is-invalid');
            if (feedback) feedback.style.display = 'none';
        }
    }

    // Smart auto-generation with AI-like suggestions
    function autoGenerateName() {
        const shiftType = document.getElementById('id_shift_type');
        const startTime = document.getElementById('id_start_time');
        const endTime = document.getElementById('id_end_time');
        const nameField = document.getElementById('id_name');

        if (shiftType && startTime && endTime && nameField && !nameField.value) {
            const type = shiftType.options[shiftType.selectedIndex]?.text || '';
            const start = startTime.value;
            const end = endTime.value;

            if (type && start && end) {
                const startHour = parseInt(start.split(':')[0]);
                let smartType = type;

                // Smart type detection based on time
                if (startHour >= 5 && startHour < 12) smartType = 'Morning';
                else if (startHour >= 12 && startHour < 17) smartType = 'Afternoon';
                else if (startHour >= 17 && startHour < 22) smartType = 'Evening';
                else smartType = 'Night';

                const generatedName = `${smartType} Shift (${start} - ${end})`;
                nameField.placeholder = generatedName;

                // Show suggestion
                const suggestion = document.getElementById('name-suggestion');
                if (suggestion) {
                    suggestion.innerHTML = `<small class="text-muted"><i class="fas fa-lightbulb text-warning me-1"></i>Suggested: <button type="button" class="btn btn-link btn-sm p-0 text-primary" onclick="document.getElementById('id_name').value='${generatedName}'">${generatedName}</button></small>`;
                }
            }
        }
    }

    // Advanced duration calculation with break time consideration
    function calculateDuration() {
        const startTime = document.getElementById('id_start_time');
        const endTime = document.getElementById('id_end_time');
        const breakTimesField = document.getElementById('id_break_times');
        const durationDisplay = document.getElementById('shift-duration-display');

        if (startTime && endTime && startTime.value && endTime.value) {
            const start = new Date(`2000-01-01T${startTime.value}`);
            const end = new Date(`2000-01-01T${endTime.value}`);

            if (end > start) {
                let totalMs = end - start;

                // Subtract break times if provided
                if (breakTimesField && breakTimesField.value.trim()) {
                    try {
                        const breaks = JSON.parse(breakTimesField.value);
                        breaks.forEach(breakItem => {
                            const breakStart = new Date(`2000-01-01T${breakItem.start}`);
                            const breakEnd = new Date(`2000-01-01T${breakItem.end}`);
                            if (breakEnd > breakStart) {
                                totalMs -= (breakEnd - breakStart);
                            }
                        });
                    } catch (e) {
                        // Ignore invalid JSON for duration calculation
                    }
                }

                const diffHrs = Math.floor(totalMs / (1000 * 60 * 60));
                const diffMins = Math.floor((totalMs % (1000 * 60 * 60)) / (1000 * 60));

                let durationText = '';
                if (diffHrs > 0) {
                    durationText += `${diffHrs} hour${diffHrs > 1 ? 's' : ''}`;
                }
                if (diffMins > 0) {
                    durationText += `${durationText ? ' ' : ''}${diffMins} minute${diffMins > 1 ? 's' : ''}`;
                }

                if (durationDisplay) {
                    durationDisplay.innerHTML = `
                        <i class="fas fa-clock text-info me-1"></i>
                        <strong>Working Duration:</strong> ${durationText}
                        <small class="text-muted ms-2">(excluding breaks)</small>
                    `;
                    durationDisplay.style.display = 'block';
                    utils.animate(durationDisplay, 'pulse');
                }
            }
        }
    }

    // Enhanced quick presets with animations
    function setupQuickPresets() {
        const presets = {
            'morning': { start: '06:00', end: '14:00', icon: 'sun', color: 'warning' },
            'afternoon': { start: '14:00', end: '22:00', icon: 'cloud-sun', color: 'primary' },
            'evening': { start: '16:00', end: '00:00', icon: 'moon', color: 'info' },
            'night': { start: '22:00', end: '06:00', icon: 'star', color: 'dark' }
        };

        const timeSection = document.querySelector('.form-section h5 i.fa-clock')?.closest('.form-section');
        if (timeSection) {
            const presetDiv = document.createElement('div');
            presetDiv.className = 'mb-4';
            presetDiv.innerHTML = `
                <label class="form-label d-flex align-items-center">
                    <i class="fas fa-magic text-primary me-2"></i>
                    Quick Presets:
                </label>
                <div class="row g-2">
                    ${Object.entries(presets).map(([key, preset]) => `
                        <div class="col-6 col-md-3">
                            <button type="button" class="btn btn-outline-${preset.color} w-100 position-relative overflow-hidden"
                                    data-preset="${key}" style="min-height: 60px;">
                                <i class="fas fa-${preset.icon} me-1"></i>
                                <div class="fw-bold">${key.charAt(0).toUpperCase() + key.slice(1)}</div>
                                <small class="text-muted">${preset.start} - ${preset.end}</small>
                            </button>
                        </div>
                    `).join('')}
                </div>
            `;

            timeSection.appendChild(presetDiv);

            presetDiv.querySelectorAll('[data-preset]').forEach(btn => {
                btn.addEventListener('click', function() {
                    const preset = presets[this.dataset.preset];
                    document.getElementById('id_start_time').value = preset.start;
                    document.getElementById('id_end_time').value = preset.end;

                    // Animate button
                    utils.animate(this, 'bounce');

                    // Trigger validations
                    validateTimes();
                    calculateDuration();
                    autoGenerateName();

                    utils.showNotification(`Applied ${this.dataset.preset} shift preset`, 'success');
                });
            });
        }
    }

    // Advanced break times helper with drag-and-drop
    function setupBreakTimesHelper() {
        const breakTimesField = document.getElementById('id_break_times');
        if (breakTimesField) {
            const helperDiv = document.createElement('div');
            helperDiv.className = 'mt-3 p-3 bg-light rounded';
            helperDiv.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <small class="text-muted fw-bold">
                        <i class="fas fa-tools me-1"></i>Break Tools:
                    </small>
                    <div class="btn-group btn-group-sm">
                        <button type="button" class="btn btn-outline-primary btn-sm" id="add-break-lunch">
                            <i class="fas fa-utensils me-1"></i>Lunch
                        </button>
                        <button type="button" class="btn btn-outline-info btn-sm" id="add-break-short">
                            <i class="fas fa-coffee me-1"></i>Short
                        </button>
                        <button type="button" class="btn btn-outline-success btn-sm" id="clear-breaks">
                            <i class="fas fa-trash me-1"></i>Clear
                        </button>
                    </div>
                </div>
                <div id="break-validation-feedback" class="mt-2" style="display: none;"></div>
            `;

            breakTimesField.parentNode.appendChild(helperDiv);

            // Add break buttons
            document.getElementById('add-break-lunch').addEventListener('click', () => addBreak('lunch'));
            document.getElementById('add-break-short').addEventListener('click', () => addBreak('short_break'));
            document.getElementById('clear-breaks').addEventListener('click', () => {
                breakTimesField.value = '';
                validateBreakTimes();
                utils.showNotification('Break times cleared', 'info');
            });

            function addBreak(type) {
                const templates = {
                    lunch: { start: "12:00", end: "13:00", type: "lunch" },
                    short_break: { start: "15:00", end: "15:15", type: "short_break" }
                };

                let breaks = [];
                if (breakTimesField.value.trim()) {
                    try {
                        breaks = JSON.parse(breakTimesField.value);
                    } catch (e) {
                        breaks = [];
                    }
                }

                breaks.push(templates[type]);
                breakTimesField.value = JSON.stringify(breaks, null, 2);
                validateBreakTimes();
                utils.showNotification(`Added ${type.replace('_', ' ')} break`, 'success');
            }
        }
    }

    // Enhanced form validation with progress tracking
    function setupFormValidation() {
        const form = document.querySelector('form');
        if (form) {
            const progressBar = document.createElement('div');
            progressBar.className = 'progress mb-3';
            progressBar.innerHTML = `
                <div class="progress-bar bg-success" role="progressbar" style="width: 0%"></div>
            `;
            form.insertBefore(progressBar, form.firstChild);

            function updateProgress() {
                const requiredFields = form.querySelectorAll('[required]');
                const filledFields = Array.from(requiredFields).filter(field => field.value.trim());
                const progress = (filledFields.length / requiredFields.length) * 100;
                progressBar.querySelector('.progress-bar').style.width = `${progress}%`;
            }

            form.addEventListener('input', utils.debounce(updateProgress, 300));
            form.addEventListener('change', updateProgress);

            form.addEventListener('submit', function(e) {
                validateTimes();
                validateBreakTimes();

                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();

                    const firstInvalid = form.querySelector(':invalid');
                    if (firstInvalid) {
                        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        firstInvalid.focus();
                        utils.animate(firstInvalid, 'shake');
                    }

                    utils.showNotification('Please fix the validation errors', 'error');
                } else {
                    // Show loading state
                    const submitBtn = form.querySelector('button[type="submit"]');
                    if (submitBtn) {
                        submitBtn.innerHTML = '<span class="spinner me-2"></span>Saving...';
                        submitBtn.disabled = true;
                    }
                }
                form.classList.add('was-validated');
            });

            updateProgress();
        }
    }

    // Event listeners with debouncing
    const startTimeField = document.getElementById('id_start_time');
    const endTimeField = document.getElementById('id_end_time');
    const breakTimesField = document.getElementById('id_break_times');
    const shiftTypeField = document.getElementById('id_shift_type');

    if (startTimeField) {
        startTimeField.addEventListener('change', utils.debounce(() => {
            validateTimes();
            calculateDuration();
            autoGenerateName();
        }, 300));
    }

    if (endTimeField) {
        endTimeField.addEventListener('change', utils.debounce(() => {
            validateTimes();
            calculateDuration();
            autoGenerateName();
        }, 300));
    }

    if (breakTimesField) {
        breakTimesField.addEventListener('input', utils.debounce(validateBreakTimes, 500));
        breakTimesField.addEventListener('blur', validateBreakTimes);
    }

    if (shiftTypeField) {
        shiftTypeField.addEventListener('change', autoGenerateName);
    }

    // Theme toggle functionality with localStorage persistence
    function setupThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        const themeIcon = document.getElementById('theme-icon');
        const body = document.body;

        if (!themeToggle || !themeIcon) return;

        // Get saved theme or default to light
        const savedTheme = localStorage.getItem('shift-form-theme') || 'light';
        const currentTheme = body.getAttribute('data-theme') || savedTheme;

        // Apply initial theme
        applyTheme(currentTheme);

        // Theme toggle event listener
        themeToggle.addEventListener('click', function() {
            const newTheme = body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);

            // Save preference
            localStorage.setItem('shift-form-theme', newTheme);

            // Animate toggle button
            utils.animate(themeToggle, 'bounce');

            // Show notification
            utils.showNotification(
                `Switched to ${newTheme} mode`,
                'info'
            );
        });

        function applyTheme(theme) {
            body.setAttribute('data-theme', theme);

            // Update icon
            if (theme === 'dark') {
                themeIcon.className = 'fas fa-sun';
                themeToggle.setAttribute('aria-label', 'Switch to light mode');
            } else {
                themeIcon.className = 'fas fa-moon';
                themeToggle.setAttribute('aria-label', 'Switch to dark mode');
            }

            // Add transition class for smooth theme switching
            body.classList.add('theme-transitioning');
            setTimeout(() => {
                body.classList.remove('theme-transitioning');
            }, 300);
        }
    }

    // Initialize all features
    setupThemeToggle();
    setupQuickPresets();
    setupBreakTimesHelper();
    setupFormValidation();
    calculateDuration();
    autoGenerateName();

    // Add duration display with enhanced styling
    const timeSection = document.querySelector('.form-section h5 i.fa-clock')?.closest('.form-section');
    if (timeSection) {
        const durationDiv = document.createElement('div');
        durationDiv.id = 'shift-duration-display';
        durationDiv.className = 'alert alert-info mt-3 border-0';
        durationDiv.style.cssText = `
            background: linear-gradient(135deg, rgba(79, 172, 254, 0.1), rgba(0, 242, 254, 0.1));
            border-left: 4px solid #4facfe;
            display: none;
        `;
        timeSection.appendChild(durationDiv);

        // Add name suggestion area
        const nameSuggestion = document.createElement('div');
        nameSuggestion.id = 'name-suggestion';
        nameSuggestion.className = 'mt-2';
        document.getElementById('id_name').parentNode.appendChild(nameSuggestion);
    }

    console.log('✨ Enhanced Shift Form loaded with modern features: validation, presets, duration calculation, and smart suggestions');
});
