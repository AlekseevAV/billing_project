from datetime import datetime

from django.conf import settings
from pytz import timezone


def set_current_timezone(input_datetime: datetime) -> datetime:
    """Set current timezone from settings to given input datetime"""
    settings_time_zone = timezone(settings.TIME_ZONE)
    return input_datetime.astimezone(settings_time_zone)
