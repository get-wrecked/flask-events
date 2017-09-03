import warnings

import pytest
from flask import Flask

from flask_canonical import CanonicalLogger


# Ensure warnings are treated as errors when running tests
warnings.filterwarnings('error', module='cachish')


def app_init_direct():
    _app = create_app()
    CanonicalLogger(_app)
    return _app


def app_factory():
    _app = create_app()
    canonical_logger = CanonicalLogger()
    canonical_logger.init_app(_app)
    return _app


def create_app():
    _app = Flask('test_app')

    @_app.route('/')
    def main_route(): # pylint: disable=unused-variable
        return 'Hello, world'

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
