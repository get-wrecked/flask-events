import socket
from unittest import mock

import pytest

from flask_events import UnitedMetric
from flask_events.outlets import LibhoneyOutlet


def test_libhoney():
    client_mock = mock.Mock()
    outlet = LibhoneyOutlet(client_mock)
    outlet.handle({'key': 'value'})

    client_mock.send_now.assert_called_with({
        'key': 'value',
        'hostname': socket.getfqdn(),
    })


@pytest.mark.parametrize('test_input,expected_output', [
    ({'time': UnitedMetric(0.123456, 'seconds')}, {'time_seconds': 0.123456}),
    ({'size': UnitedMetric(1234, 'bytes')}, {'size_bytes': 1234}),
])
def test_libhoney_units(test_input, expected_output):
    client_mock = mock.Mock()
    outlet = LibhoneyOutlet(client_mock)
    outlet.handle(test_input)

    expected_output.update({
        'hostname': socket.getfqdn(),
    })

    client_mock.send_now.assert_called_with(expected_output)
