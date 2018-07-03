from ..events import UnitedMetric


class LibhoneyOutlet(object):

    def __init__(self, libhoney_client):
        self.libhoney_client = libhoney_client


    def handle(self, event_data):
        formatted_data = {}
        for key, val in event_data.items():
            if isinstance(val, UnitedMetric):
                formatted_data['%s_%s' % (key, val.unit)] = val.value
            else:
                formatted_data[key] = val

        self.libhoney_client.send_now(formatted_data)
