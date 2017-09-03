import warnings
import shutil
import tempfile

import pytest
from flask import Flask

from flask_canonical import CanonicalLogger


# Ensure warnings are treated as errors when running tests
warnings.filterwarnings('error', module='cachish')


def app_init_direct():
    _app = create_app()
    canonical_logger = CanonicalLogger(_app)
    return _app


def app_factory():
    _app = create_app()
    canonical_logger = CanonicalLogger()
    canonical_logger.init_app(_app)
    return _app


def create_app():
    app = Flask('test_app')

    @app.route('/')
    def main_route():
        return 'Hello, world'

    return app


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
