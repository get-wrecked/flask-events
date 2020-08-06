import re

import pytest
from testfixtures import LogCapture

from sample_app import create_app, db

# pylint: disable=redefined-outer-name


def test_sample_app(sample_app_client):
    with LogCapture() as logs:
        response = sample_app_client.get('/')

    assert response.status_code == 200
    assert len(logs.records) == 1
    assert 'method=GET path=/ status=200' in logs.records[0].msg
    assert 'database_query_time=' in logs.records[0].msg


def test_sample_app_add_random(sample_app_client):
    with LogCapture() as logs:
        response = sample_app_client.post('/add-random')

    assert response.status_code == 302
    assert 'method=POST path=/add-random status=302' in logs.records[0].msg

    assert 'database_executes=1' in logs.records[0].msg
    assert_matches(r'database_query_time=0.00\ds', logs.records[0].msg)


def test_sample_app_abort(sample_app_client):
    with LogCapture() as logs:
        response = sample_app_client.get('/abort')

    assert response.status_code == 503
    assert 'path=/abort status=503' in logs.records[0].msg
    assert 'database_query_time=' not in logs.records[0].msg


def test_sample_app_crash(sample_app_client):
    with LogCapture() as logs:
        response = sample_app_client.get('/crash')

    assert response.status_code == 500
    assert len(logs.records) == 2 # flask also logs the error
    assert logs.records[0].name == 'sample_app' # The flask default logger
    assert logs.records[1].name == 'sample_app.canonical'
    assert 'error=ValueError error_msg="no message"' in logs.records[1].msg


def assert_matches(regex, message):
    assert re.search(regex, message) is not None


@pytest.fixture
def sample_app():
    app = create_app()

    with app.app_context():
        db.create_all()

    return app


@pytest.fixture
def sample_app_client(sample_app):
    return sample_app.test_client()
