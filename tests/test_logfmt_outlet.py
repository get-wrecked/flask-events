from collections import OrderedDict

import pytest
from testfixtures import LogCapture


from flask_events.outlets.logfmt import LogfmtOutlet

# pylint: disable=redefined-outer-name


def test_logfmt(outlet):
    event_data = OrderedDict((('key', 'value'), ('foo', 'bar')))
    with LogCapture() as logs:
        outlet.handle(event_data, {}, {})

    assert len(logs.records) == 1
    record = logs.records[0]
    assert record.msg == 'key=value foo=bar' # measure#timing=0.123s'
    assert record.name == 'test_app.canonical'
    assert record.levelname == 'INFO'


@pytest.mark.parametrize('event_data,expected_output', [
    ({'somekey': 1}, 'somekey=1'),
    ({'empty': None}, 'empty='),
    ({'mykey': 'my custom value'}, 'mykey="my custom value"'),
])
def test_logfmt_formatting(event_data, expected_output, outlet):
    with LogCapture() as logs:
        outlet.handle(event_data, {}, {})

    assert logs.records[0].msg == expected_output


def test_logfmt_measurements(outlet):
    with LogCapture() as logs:
        outlet.handle({}, {'measurement': 0.123456}, {})
    assert logs.records[0].msg == 'measure#measurement=0.123s'


def test_logfmt_samples(outlet):
    with LogCapture() as logs:
        outlet.handle({}, {}, {'sample': 'foo'})
    assert logs.records[0].msg == 'sample#sample=foo'


@pytest.fixture
def outlet():
    return LogfmtOutlet('test_app')
