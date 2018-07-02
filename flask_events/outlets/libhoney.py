class LibhoneyOutlet(object):

    def __init__(self, libhoney_client):
        self.libhoney_client = libhoney_client


    def handle(self, event_data, measurements, samples):
        self.libhoney_client.send_now(event_data)
