import re

from logging import getLogger

NEEDS_QUOTES_RE = re.compile(r'[\s=]')


class LogfmtOutlet(object):

    def __init__(self, app):
        self.logger = getLogger('%s.canonical' % app.name)


    def handle(self, event_data, measures, samples):
        for key, val in measures.items():
            event_data['measure#%s' % key] = '%.3fs' % val

        for key, val in samples.items():
            event_data['sample#%s' % key] = val

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
