from unittest import mock

from flask_events.outlets import LibhoneyOutlet


def test_libhoney():
    client_mock = mock.Mock()
    outlet = LibhoneyOutlet(client_mock)
    outlet.handle({'key': 'value'}, {}, {})

    client_mock.send_now.assert_called_with({
        'key': 'value',
    })


def test_libhoney_measures():
    client_mock = mock.Mock()
    outlet = LibhoneyOutlet(client_mock)
    outlet.handle({}, {'request_time': 0.123456}, {})

    client_mock.send_now.assert_called_with({
        'request_time_seconds': 0.123456,
    })


def test_libhoney_samples():
    client_mock = mock.Mock()
    outlet = LibhoneyOutlet(client_mock)
    outlet.handle({}, {}, {'request_size': 123456})

    client_mock.send_now.assert_called_with({
        'request_size_bytes': 123456,
    })
