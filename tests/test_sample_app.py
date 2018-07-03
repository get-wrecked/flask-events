import pytest

from testfixtures import LogCapture

from sample_app import create_app, db


def test_sample_app(sample_app_client):
    with LogCapture() as logs:
        response = sample_app_client.get('/')

    assert response.status_code == 200
    assert len(logs.records) == 1
    assert 'path=/ status=200' in logs.records[0].msg


@pytest.fixture
def sample_app():
    app = create_app()

    with app.app_context():
        db.create_all()

    return app


@pytest.fixture
def sample_app_client(sample_app):
    return sample_app.test_client()
