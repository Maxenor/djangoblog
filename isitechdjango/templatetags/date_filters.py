from django import template
from django.utils import timezone
from django.utils.translation import gettext as _
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def humanize_date(value):
    """
    Convert a datetime to a human-readable relative time format
    Examples: "il y a 2 heures", "hier", "la semaine dernière"
    """
    if not value:
        return ""
    
    # Convert to timezone-aware datetime if needed
    if timezone.is_naive(value):
        value = timezone.make_aware(value)
    
    now = timezone.now()
    diff = now - value
    
    # Future dates
    if diff.total_seconds() < 0:
        return _("in the future")
    
    # Less than 1 minute
    if diff.total_seconds() < 60:
        return _("just now")
    
    # Less than 1 hour
    if diff.total_seconds() < 3600:
        minutes = int(diff.total_seconds() / 60)
        if minutes == 1:
            return _("1 minute ago")
        return _("{} minutes ago").format(minutes)
    
    # Less than 24 hours (same day)
    if diff.days == 0:
        hours = int(diff.total_seconds() / 3600)
        if hours == 1:
            return _("1 hour ago")
        return _("{} hours ago").format(hours)
    
    # Yesterday
    if diff.days == 1:
        return _("yesterday")
    
    # Less than 1 week
    if diff.days < 7:
        return _("{} days ago").format(diff.days)
    
    # Less than 1 month
    if diff.days < 30:
        weeks = diff.days // 7
        if weeks == 1:
            return _("1 week ago")
        return _("{} weeks ago").format(weeks)
    
    # Less than 1 year
    if diff.days < 365:
        months = diff.days // 30
        if months == 1:
            return _("1 month ago")
        return _("{} months ago").format(months)
    
    # More than 1 year
    years = diff.days // 365
    if years == 1:
        return _("1 year ago")
    return _("{} years ago").format(years)

@register.filter
def smart_date(value):
    """
    Intelligent date display with both relative and absolute formats
    """
    if not value:
        return ""
    
    relative = humanize_date(value)
    absolute = value.strftime("%d/%m/%Y à %H:%M")
    
    return f'<span title="{absolute}">{relative}</span>'

@register.simple_tag
def reading_time_text(minutes):
    """
    Convert reading time to human-readable text
    """
    if minutes == 1:
        return _("1 minute read")
    elif minutes < 60:
        return _("{} minutes read").format(minutes)
    else:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if hours == 1 and remaining_minutes == 0:
            return _("1 hour read")
        elif hours == 1:
            return _("1 hour {} minutes read").format(remaining_minutes)
        elif remaining_minutes == 0:
            return _("{} hours read").format(hours)
        else:
            return _("{} hours {} minutes read").format(hours, remaining_minutes)
