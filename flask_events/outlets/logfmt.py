import re
from logging import getLogger

from ..events import UnitedMetric


NEEDS_QUOTES_RE = re.compile(r'[\s=]')


class LogfmtOutlet(object):

    def __init__(self, base_logger):
        self.logger = getLogger('%s.canonical' % base_logger)


    def handle(self, event_data):
        for key, val in event_data.items():
            if isinstance(val, UnitedMetric):
                if val.unit == 'seconds':
                    event_data[key] = '%.3fs' % val.value
                else:
                    event_data[key] = '%s%s' % (val.value, val.unit)

        self.logger.info(' '.join(
            format_key_value_pair(key, val) for (key, val) in event_data.items())
        )


def format_key_value_pair(key, value):
    if value:
        value = str(value)
    else:
        value = ''

    should_quote = NEEDS_QUOTES_RE.search(value)

    if should_quote:
        value = '"%s"' % value

    return '%s=%s' % (key, value)
