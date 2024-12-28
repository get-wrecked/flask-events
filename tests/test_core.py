import os
from unittest import mock

import pytest
from flask import Flask

from flask_events import Events, UnitedMetric

from .conftest import app_factory, create_app, CapturingOutlet


def test_logger_unconfigured(client):
    response = client.get('/')
    assert response.status_code == 200

    test_outlet = client.application.test_outlet
    assert test_outlet.event_data['fwd'] == '127.0.0.1'
    assert test_outlet.event_data['method'] == 'GET'
    assert test_outlet.event_data['request_user_agent'].startswith('Werkzeug')
    assert test_outlet.event_data['status'] == 200
    assert 0 < test_outlet.event_data['request_total'].value < 0.100
    assert test_outlet.event_data['handler'] == 'tests.conftest.create_app.<locals>.main_route'



@pytest.mark.parametrize('forwarded_for,expected', [
    ('1.2.3.4,5.6.7.8', '1.2.3.0,5.6.7.8'),
    ('2001:1db8:85a3:3a4b:1a2a:8a2e:0370:7334', '2001:1db8:85a3::'),
])
def test_anonymize_ips(forwarded_for, expected):
    app = create_app()
    app.config['EVENTS_ANONYMIZE_IPS'] = True
    events = Events(app)
    app.test_outlet = CapturingOutlet()
    events.outlets = [app.test_outlet]
    with app.test_client() as client:
        response = client.get('/', headers={
            'X-Forwarded-For': forwarded_for,
        })
    assert response.status_code == 200
    assert client.application.test_outlet.event_data['fwd'] == expected


@pytest.mark.parametrize('forwarded_for,expected', [
    ('1.2.3.4,5.6.7.8', '1.2.0.0,5.6.7.8'),
    ('2001:1db8:85a3:3a4b:1a2a:8a2e:0370:7334', '2001:1db8:85a3:3a4b::'),
])
def test_anonymize_ips_custom_masks(forwarded_for, expected):
    app = create_app()
    app.config['EVENTS_ANONYMIZE_IPS'] = {
        'ipv4_mask': '255.255.0.0',
        'ipv6_mask': 'ffff:ffff:ffff:ffff:0000:0000:0000:0000', # preserves the SLA
    }
    events = Events(app)
    app.test_outlet = CapturingOutlet()
    events.outlets = [app.test_outlet]
    with app.test_client() as client:
        response = client.get('/', headers={
            'X-Forwarded-For': forwarded_for,
        })
    assert response.status_code == 200
    assert client.application.test_outlet.event_data['fwd'] == expected


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


def test_add_all(app):
    app.events.add_all('version', 2)
    with app.test_request_context('/'):
        app.preprocess_request()

    assert app.test_outlet.event_data['version'] == 2


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


def test_honeycomb_init():
    app = Flask('test_app')
    app.config['EVENTS_HONEYCOMB_KEY'] = 'foobar'

    events = Events()
    events.init_app(app)

    assert len(events.outlets) == 2
    assert events.outlets[1].libhoney_client.writekey == 'foobar'
    assert events.outlets[1].libhoney_client.dataset == 'test_app'


def test_default_heroku_env():
    mock_env = {
        'HEROKU_RELEASE_VERSION': 'v12',
        'HEROKU_SLUG_COMMIT': '5ca1ab1e',
    }
    with mock.patch.dict(os.environ, mock_env):
        app = app_factory()
        with app.test_request_context('/'):
            app.preprocess_request()
        assert app.test_outlet.event_data['release_version'] == 'v12'
        assert app.test_outlet.event_data['slug_commit'] == '5ca1ab1e'


def test_instrument_func(app):
    @app.events.instrument()
    def some_func(first_arg, *args, **kwargs): # pylint: disable=unused-argument
        pass

    with app.app_context():
        some_func('bar', 'zoo', thing=2)

    assert app.test_outlet.event_data['func_name'] == 'some_func'
    assert app.test_outlet.event_data['first_arg'] == 'bar'
    assert app.test_outlet.event_data['args_0'] == 'zoo'
    assert app.test_outlet.event_data['thing'] == 2
    assert 'duration' in app.test_outlet.event_data
    assert 'error' not in app.test_outlet.event_data


def test_instrument_func_with_exception(app):
    @app.events.instrument()
    def some_func():
        raise ValueError('thing broke')

    with app.app_context():
        try:
            some_func()
        except ValueError:
            pass

    assert app.test_outlet.event_data['func_name'] == 'some_func'
    assert app.test_outlet.event_data['error'] == 'ValueError'
    assert app.test_outlet.event_data['error_msg'] == 'thing broke'
    assert 'duration' in app.test_outlet.event_data
