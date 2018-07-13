from collections import OrderedDict

import pytest
from testfixtures import LogCapture

from flask_events import UnitedMetric
from flask_events.outlets.logfmt import LogfmtOutlet

# pylint: disable=redefined-outer-name


def test_logfmt(outlet):
    event_data = OrderedDict((('key', 'value'), ('foo', 'bar')))
    with LogCapture() as logs:
        outlet.handle(event_data)

    assert len(logs.records) == 1
    record = logs.records[0]
    assert record.msg == 'key=value foo=bar' # measure#timing=0.123s'
    assert record.name == 'test_app.canonical'
    assert record.levelname == 'INFO'


@pytest.mark.parametrize('event_data,expected_output', [
    ({'somekey': 1}, 'somekey=1'),
    ({'somekey': 0}, 'somekey=0'),
    ({'empty': None}, 'empty='),
    ({'true': True}, 'true=true'),
    ({'false': False}, 'false=false'),
    ({'float': 1.23456789}, 'float=1.2346'),
    ({'mykey': 'my custom value'}, 'mykey="my custom value"'),
])
def test_logfmt_formatting(event_data, expected_output, outlet):
    with LogCapture() as logs:
        outlet.handle(event_data)

    assert logs.records[0].msg == expected_output


def test_logfmt_unit_seconds(outlet):
    with LogCapture() as logs:
        outlet.handle({'measurement': UnitedMetric(0.123456, 'seconds')})
    assert logs.records[0].msg == 'measurement=0.123s'


def test_logfmt_unit_bytes(outlet):
    with LogCapture() as logs:
        outlet.handle({'size': UnitedMetric(123456, 'bytes')})
    assert logs.records[0].msg == 'size=120.6kB'


def test_logfmt_unit_unknown_unit(outlet):
    with LogCapture() as logs:
        outlet.handle({'thing': UnitedMetric(3, 'foobars')})
    assert logs.records[0].msg == 'thing=3foobars'


@pytest.fixture
def outlet():
    return LogfmtOutlet('test_app')
