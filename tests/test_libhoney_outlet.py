from unittest import mock

from flask_events.outlets import LibhoneyOutlet


def test_libhoney():
    client_mock = mock.Mock()
    outlet = LibhoneyOutlet(client_mock)
    outlet.handle({'key': 'value'}, {}, {})

    client_mock.send_now.assert_called_with({
        'key': 'value',
    })
