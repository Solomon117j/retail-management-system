#!/usr/bin/env python
import os
import sys
import django
from datetime import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_management_system.settings')
django.setup()

from human_resources.models import CostCenter, Shift

def test_models():
    print('Testing model functionality...')

    # Test CostCenter creation
    try:
        cc = CostCenter.objects.create(
            name='Test Center 3',
            code='TC003',
            description='Test cost center'
        )
        print(f'✓ CostCenter created: {cc}')
    except Exception as e:
        print(f'✗ CostCenter creation failed: {e}')
        return False

    # Test Shift creation with new fields
    try:
        s = Shift.objects.create(
            name='Test Shift 3',
            shift_type='morning',
            start_time=time(9, 0),
            end_time=time(17, 0),
            break_times='[{"start": "12:00", "end": "13:00", "type": "lunch"}]',
            overtime_rules='Standard overtime rules',
            cost_center=cc,
            approval_required=True,
            approval_levels=2
        )
        print(f'✓ Shift created: {s}')
        print(f'✓ Shift break duration: {s.total_break_duration}')
    except Exception as e:
        print(f'✗ Shift creation failed: {e}')
        return False

    # Test property calculations
    try:
        assert s.total_break_duration == 1.0, f"Expected 1.0, got {s.total_break_duration}"
        print('✓ Break duration calculation correct')
    except Exception as e:
        print(f'✗ Break duration calculation failed: {e}')
        return False

    print('✓ All model functionality tests passed')
    return True

if __name__ == '__main__':
    success = test_models()
    sys.exit(0 if success else 1)
