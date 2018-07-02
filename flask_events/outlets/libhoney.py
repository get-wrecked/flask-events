class LibhoneyOutlet(object):

    def __init__(self, libhoney_client):
        self.libhoney_client = libhoney_client


    def handle(self, event_data, measurements, samples):
        for key, val in measurements.items():
            event_data['%s_seconds' % key] = val

        for key, val in samples.items():
            event_data['%s_bytes' % key] = val

        self.libhoney_client.send_now(event_data)
