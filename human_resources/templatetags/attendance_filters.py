from django import template
import datetime

register = template.Library()

@register.filter
def time_diff(end_time, start_time):
    """Calculate time difference between two time objects"""
    if not end_time or not start_time:
        return ""
    
    # Create datetime objects with arbitrary same date
    base_date = datetime.date(2023, 1, 1)
    start_dt = datetime.datetime.combine(base_date, start_time)
    end_dt = datetime.datetime.combine(base_date, end_time)
    
    # Handle overnight shifts
    if end_dt < start_dt:
        end_dt += datetime.timedelta(days=1)
    
    # Calculate duration
    delta = end_dt - start_dt
    total_seconds = delta.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    
    return f"{hours}:{minutes:02d}"