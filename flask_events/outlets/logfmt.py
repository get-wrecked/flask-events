import re

from logging import getLogger

NEEDS_QUOTES_RE = re.compile(r'[\s=]')


class LogfmtOutlet(object):

    def __init__(self, app):
        self.logger = getLogger('%s.canonical' % app.name)


    def handle(self, event_data):
        log_line_items = (format_key_value_pair(key, val) for (key, val) in event_data.items())
        self.logger.info(' '.join(log_line_items))


def format_key_value_pair(key, value):
    if value:
        value = str(value)
    else:
        value = ''

    should_quote = NEEDS_QUOTES_RE.search(value)

    if should_quote:
        value = '"%s"' % value

    return '%s=%s' % (key, value)
