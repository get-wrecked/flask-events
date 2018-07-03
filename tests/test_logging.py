from flask_events import UnitedMetric


def test_logger_unconfigured(client):
    response = client.get('/')
    assert response.status_code == 200

    test_outlet = client.application.test_outlet
    assert test_outlet.event_data['fwd'] == '127.0.0.1'
    assert test_outlet.event_data['method'] == 'GET'
    assert test_outlet.event_data['request_user_agent'].startswith('werkzeug')
    assert test_outlet.event_data['status'] == 200
    assert 0 < test_outlet.event_data['request_total'].value < 0.100


def test_add(app):
    with app.test_request_context('/'):
        app.preprocess_request()
        app.events.add('key', 'value')

    assert app.test_outlet.event_data['key'] == 'value'


def test_add_with_unit(app):
    with app.test_request_context('/'):
        app.preprocess_request()
        app.events.add('time', 1.23, unit='seconds')

    assert app.test_outlet.event_data['time'] == UnitedMetric(1.23, 'seconds')


def test_includes_request_id(client):
    response = client.get('/', headers={
        'x-request-id': 'myrequestid',
    })
    assert response.status_code == 200

    assert client.application.test_outlet.event_data['request_id'] == 'myrequestid'


def test_aborted_view(client):
    response = client.get('/abort')
    assert response.status_code == 503

    assert client.application.test_outlet.event_data['status'] == 503


def test_invalid_utf8(client):
    response = client.get(b'/?param=\xEA')
    assert response.status_code == 200

    assert client.application.test_outlet.event_data['path'] == '/?param=\\xea'
