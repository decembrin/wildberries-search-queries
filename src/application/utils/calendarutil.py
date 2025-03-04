import calendar
import functools
from datetime import date, datetime, timezone
from threading import local

import pytz

from config import Settings

settings = Settings()

# UTC time zone as a tzinfo instance.
utc = pytz.utc


# In order to avoid accessing settings at compile time,
# wrap the logic in a function and cache the result.
@functools.lru_cache(maxsize=128)
def get_default_timezone():
    """
    Return the default time zone as a tzinfo instance.

    This is the time zone defined by settings.TIME_ZONE.
    """
    return pytz.timezone(settings.time_zone)


_active = local()


def get_current_timezone():
    """
    Return the currently active time zone as a tzinfo instance.
    """
    return getattr(_active, 'value', get_default_timezone())


# Utilities

def now():
    """
    Return an aware or naive datetime.datetime, depending on settings.use_tz.
    """
    if settings.use_tz:
        # timeit shows that datetime.now(tz=utc) is 24% slower
        return datetime.now(timezone.utc).replace(tzinfo=utc)
    else:
        return datetime.now()


def unix():
    return get_start_of_year(now()).replace(year=1970)


def localtime(value=None, timezone=None):
    """
    Convert an aware datetime.datetime to local time.

    Only aware datetimes are allowed. When value is omitted, it defaults to
    now().

    Local time is defined by the current time zone, unless another time zone
    is specified.
    """
    if value is None:
        value = now()
    if timezone is None:
        timezone = get_current_timezone()
    # Emulate the behavior of astimezone() on Python < 3.6.
    if is_naive(value):
        raise ValueError('localtime() cannot be applied to a naive datetime')
    return value.astimezone(timezone)


# By design, these four functions don't perform any checks on their arguments.
# The caller should ensure that they don't receive an invalid value like None.

def is_aware(value):
    """
    Determine if a given datetime.datetime is aware.

    The concept is defined in Python's docs:
    https://docs.python.org/library/datetime.html#datetime.tzinfo

    Assuming value.tzinfo is either None or a proper datetime.tzinfo,
    value.utcoffset() implements the appropriate logic.
    """
    return value.utcoffset() is not None


def is_naive(value):
    """
    Determine if a given datetime.datetime is naive.

    The concept is defined in Python's docs:
    https://docs.python.org/library/datetime.html#datetime.tzinfo

    Assuming value.tzinfo is either None or a proper datetime.tzinfo,
    value.utcoffset() implements the appropriate logic.
    """
    return value.utcoffset() is None


def make_aware(value, timezone=None, is_dst=None):
    """
    Make a naive datetime.datetime in a given time zone aware.
    """
    if timezone is None:
        timezone = get_current_timezone()
    if hasattr(timezone, 'localize'):
        # This method is available for pytz time zones.
        return timezone.localize(value, is_dst=is_dst)
    else:
        # Check that we won't overwrite the timezone of an aware datetime.
        if is_aware(value):
            raise ValueError('make_aware expects a naive datetime, got %s' % value)
        # This may be wrong around DST changes!
        return value.replace(tzinfo=timezone)


def get_start_of_day(value, localtime=False):
    if isinstance(value, datetime):
        value = value.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
    elif isinstance(value, date):
        value = value

    return value


def get_end_of_day(value, localtime=False):
    if isinstance(value, datetime):
        value = value.replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
        )
    elif isinstance(value, date):
        value = value

    return value


def get_start_of_month(value):
    return get_start_of_day(value) \
        .replace(day=1)


def get_end_of_month(dt):
    __, last_day = calendar.monthrange(dt.year, dt.month)

    return get_end_of_day(dt) \
        .replace(day=last_day)


def get_start_of_year(dt):
    return get_start_of_month(dt) \
        .replace(month=1)

def get_end_of_year(dt):
    return get_end_of_month(dt) \
        .replace(month=12)
