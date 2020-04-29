import dateutil
import pytz

def time2utc(time):
    """Convert the time array (s: datetime, tz: timezone) into a datetime w/ timezone."""
    timestamp = time['s']
    timezone = time['tz']
    return dateutil.parser.parse("{}{}".format(timestamp, timezone)).astimezone(pytz.utc)
