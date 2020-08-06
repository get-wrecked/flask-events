import warnings

import pytest
from flask import Flask, abort

from flask_events import Events


# Ensure warnings are treated as errors when running tests
warnings.filterwarnings('error', module='flask_events')

class CapturingOutlet:
    def __init__(self):
        self.event_data = None


    def handle(self, event_data):
        self.event_data = event_data


def app_init_direct():
    _app = create_app()
    _app.events = Events(_app)
    _app.test_outlet = CapturingOutlet()
    _app.events.outlets = [_app.test_outlet]
    return _app


def app_factory():
    _app = create_app()
    _app.events = Events()
    _app.events.init_app(_app)
    _app.test_outlet = CapturingOutlet()
    _app.events.outlets = [_app.test_outlet]
    return _app


def create_app():
    _app = Flask('test_app')

    @_app.route('/')
    def main_route(): # pylint: disable=unused-variable
        return 'Hello, world'

    @_app.route('/abort')
    def crash(): # pylint: disable=unused-variable
        raise abort(503)

    return _app


APPS = [
    app_init_direct,
    app_factory,
]

@pytest.fixture(params=APPS)
def app(request):
    return request.param()


@pytest.fixture
def client(app): # pylint: disable=redefined-outer-name
    return app.test_client()
