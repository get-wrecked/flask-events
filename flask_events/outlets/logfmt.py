from logging import getLogger


class LogfmtOutlet(object):

    def __init__(self, app):
        self.logger = getLogger('%s.canonical' % app.name)


    def handle(self, event_data):
        self.logger.info(' '.join(event_data))
