import socket

from ..events import UnitedMetric


class LibhoneyOutlet:

    def __init__(self, libhoney_client):
        self.libhoney_client = libhoney_client
        self.default_data = get_default_data()


    def handle(self, event_data):
        formatted_data = self.default_data.copy()
        for key, val in event_data.items():
            if isinstance(val, UnitedMetric):
                formatted_data['%s_%s' % (key, val.unit)] = val.value
            else:
                formatted_data[key] = val

        self.libhoney_client.send_now(formatted_data)


def get_default_data():
    '''This is data we add by default that is not needed for other outlets'''
    return {
        'hostname': socket.getfqdn(),
    }
